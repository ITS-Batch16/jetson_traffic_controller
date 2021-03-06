import numpy as np
import os
import cv2
import time
from config import config

from utils.utils import draw_boxes

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class WeightType(object):
    '''
    classdocs
    '''

    TRT = 'TRT'
    CAFFE = 'CAFFE'
    UFF = 'UFF'
    TRT_ENGINE = 'TRT_ENGINE'

# Simple helper data class that's a little nicer to use than a 2-tuple.
class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()


class Tensorrt(object):
    '''
    classdocs
    '''

    def __init__(self,weights_file, num_colors, net_height, net_width, inputs=None, outputs=None, workspace_size=10000000,
                 gpu_id=0, batch_size=1, fp16_mode = True, weight_file_type=WeightType.TRT_ENGINE):
        '''
        Constructor
        '''
        # This import causes pycuda to automatically manage CUDA context creation and cleanup.
        os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        import pycuda.autoinit
        import tensorrt as trt
        import pycuda.driver as cuda      

        # You can set the logger severity higher to suppress messages (or lower to display more messages).
        self.TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

        self.trt = trt
        self.cuda = cuda
        print("TRT type: {}".format(weight_file_type))
        if weight_file_type == WeightType.UFF:
            self.engine = self.build_engine_from_uff(weights_file, num_colors, net_height, net_width, workspace_size,
                                            batch_size, fp16_mode, inputs, outputs)
        elif weight_file_type == WeightType.TRT_ENGINE:
            with open(weights_file, "rb") as f, trt.Runtime(self.TRT_LOGGER) as runtime:
                self.engine = runtime.deserialize_cuda_engine(f.read())

        self.inputs, self.outputs, self.bindings, self.stream, self.output_shapes = self.allocate_buffers(self.engine)
        self.context = self.engine.create_execution_context()

    def build_engine_from_uff(self, model_file, num_colors, net_height, net_width, workspace_size,
                     batch_size, fp16_mode, inputs, outputs):
        # For more information on TRT basics, refer to the introductory samples.
        with self.trt.Builder(self.TRT_LOGGER) as builder, builder.create_network() as network, self.trt.UffParser() as parser:
            builder.max_workspace_size = workspace_size
            builder.max_batch_size = batch_size
            #builder.int8_calibrator = trt.Int8LegacyCalibrator()
            builder.fp16_mode = fp16_mode
            #builder.int8_mode = True

            # Parse the Uff Network
            for input_tensor in inputs:
                parser.register_input(input_tensor, (num_colors, net_height, net_width))
            for output in outputs:
                parser.register_output(output)
            parser.parse(model_file, network)
            # Build and return an engine.

            engine = builder.build_cuda_engine(network)
           # 
            with open("./engines/fp16.engine", "wb") as f:
                f.write(engine.serialize())
            print("Build engine done!")
            return engine

    def build_engine_from_trt(self, input_shape, workspace_size, batch_size, fp16_mode):
        # For more information on TRT basics, refer to the introductory samples.
        with self.trt.Builder(self.TRT_LOGGER) as builder, builder.create_network() as network:
            builder.max_workspace_size = workspace_size
            builder.max_batch_size = batch_size
            # builder.int8_calibrator = trt.Int8LegacyCalibrator()
            builder.fp16_mode = fp16_mode
            input_tensor = network.add_input(name='data', dtype=self.trt.float16, shape=input_shape)
            X = self.pe_trt.build_network(network,input_tensor)
            for x in X:
                network.mark_output(tensor=x.get_output(0))

            engine = builder.build_cuda_engine(network)
            
            #with open("pose_fp32.trt", "wb") as f:
                #f.write(engine.serialize())

            return engine


    # Allocates all buffers required for an engine, i.e. host/device inputs/outputs.
    def allocate_buffers(self, engine):
        inputs = []
        outputs = []
        output_shapes = []
        bindings = []
        stream = self.cuda.Stream()
        for binding in engine:
            shape = engine.get_binding_shape(binding)
            size = self.trt.volume(shape) * engine.max_batch_size
            dtype = self.trt.nptype(engine.get_binding_dtype(binding))
            # Allocate host and device buffers
            host_mem = self.cuda.pagelocked_empty(size, dtype)
            device_mem = self.cuda.mem_alloc(host_mem.nbytes)
            # Append the device buffer to device bindings.
            bindings.append(int(device_mem))
            # Append to the appropriate list.
            if engine.binding_is_input(binding):
                inputs.append(HostDeviceMem(host_mem, device_mem))
            else:
                outputs.append(HostDeviceMem(host_mem, device_mem))
                output_shapes.append(shape)
        return inputs, outputs, bindings, stream, output_shapes

    def predict(self, input_img, batch_size=1):
        #engine = self.build_engine('tftrt.uff')
        # Build an engine, allocate buffers and create a stream.
        # For more information on buffer allocation, refer to the introductory samples.
        inputs, outputs, bindings, stream, output_size = self.allocate_buffers(self.engine)
        # for i in range(len(inputs)):
            # np.copyto(inputs[i].host, inputs[i])
        
        np.copyto(inputs[0].host, input_img)

        # For more information on performing inference, refer to the introductory samples.
        # The common.do_inference function will return a list of outputs - we only have one in this case.
        # [output] = self.do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
        return self.do_inference(self.context, bindings=bindings, inputs=inputs, outputs=outputs,
                                 stream=stream, batch_size=batch_size)

    # This function is generalized for multiple inputs/outputs.
    # inputs and outputs are expected to be lists of HostDeviceMem objects.
    def do_inference(self, context, bindings, inputs, outputs, stream, batch_size):
        # Transfer input data to the GPU.
        [self.cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
        # Run inference.
        context.execute_async(batch_size=batch_size, bindings=bindings, stream_handle=stream.handle)
        # Transfer predictions back from the GPU.
        [self.cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
        # Synchronize the stream
        stream.synchronize()
        # Return only the host outputs.
        return [out.host for out in outputs]


#A CNN class which uses Tensorrt object and simplifies the operation
class CNN(object):
    def __init__(self, batch_size=4):
        '''Constructor'''
        self.batch_size = batch_size
        self.cnn = Tensorrt(
            weights_file=f'./engines/fp16_batch{batch_size}.engine',
            num_colors=3, net_height=config.H_NN_INPUT,
            net_width=config.W_NN_INPUT, inputs=['input_1'], 
            outputs=['lambda_1/Identity'], 
            batch_size=self.batch_size
            )
        # self.cnn = Tensorrt(weights_file='./models/model.uff', num_colors=3, net_height=256, net_width=384, inputs=['input_1'], outputs=['lambda_1/Identity'], batch_size=2, weight_file_type=WeightType.UFF)
        print('TRT Engine initiated successfully.')

    def preprocess_image(self, image):
        '''Preprocess an image to be feeded to the CNN and return it'''
        image = image / 255.
        image = image[:, :, ::-1]
        image = np.expand_dims(image, 0) #Expanding image dimension
        image = np.transpose(image, (0,3,1,2))
        image = image.ravel() #Flattening the image array because TRT gets a flattened array as input
        return image

    def batch_pre_process(self, x_list):
        '''Preprocess a list of images to be feeded to the CNN as a batch and return the array'''
        dim = config.W_NN_INPUT *config.H_NN_INPUT*3
        img_rz_batch = np.zeros((len(x_list),dim), dtype=np.float16)
        for j, x in enumerate(x_list):
            img_rz = x / 255.0
            img_rz = cv2.resize(img_rz, (config.W_NN_INPUT, config.H_NN_INPUT))
            img_rz = img_rz[:, :, ::-1]
            img_rz = np.expand_dims(img_rz, 0)
            img_rz = np.transpose(img_rz, (0,3, 1, 2))
            img_rz = img_rz.ravel()
            img_rz_batch[j] = img_rz
        return img_rz_batch
    
    def predict(self, image):
        '''Take an image as input and returns the reshaped CNN output'''
        image = self.preprocess_image(image)
        netout = self.cnn.predict(image)
        net_out = netout[0].reshape(8,12,5,9) #Reshaping the 1D array to the required 4D array
        return net_out
    
    def batch_predict(self, x_list):
        '''Take a list of images as input and returns the batch processed CNN output'''
        img_rz_batch = self.batch_pre_process(x_list)
        batch_pred = self.cnn.predict(img_rz_batch.ravel(), batch_size=self.batch_size)
        return batch_pred[0].reshape(self.batch_size,4320)
    
    def show_on_image(self, image, batch_size=1):
        '''Takes an input as image and shows the bounding boxes after feeding it through the CNN'''
        boxes = self.predict(image)
        image = draw_boxes(image, boxes, labels=config.LABELS)
        cv2.imshow('CNN Output',image)
        cv2.waitKey(0)

if __name__ == "__main__":
    cnn = CNN(batch_size=2)
