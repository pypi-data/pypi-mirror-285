import os
import platform

import sys
current_module = sys.modules[__name__]

# import torch to load in directml
import torch
from torch.storage import _StorageBase
from torch._C import default_generator

# Load the directml dll into the process
platform = 'win' if platform.system() == 'Windows' else 'linux'
if platform == 'win':
    directml_dll = os.path.join(os.path.dirname(__file__), 'DirectML.dll')
else:
    directml_dll = os.path.join(os.path.dirname(__file__), 'libdirectml.so')
torch.ops.load_library(directml_dll)

# import native apis
import torch_directml_native

from .device import *
from .functions import *

# # Register backend to support AMP
class PrivateUse1Module:
    @staticmethod
    def is_available():
        return True

    @staticmethod
    def is_autocast_enabled():
        return False

    @staticmethod
    def get_autocast_dtype():
        return torch.float16

    @staticmethod
    def set_autocast_enabled(enable):
        pass

    @staticmethod
    def set_autocast_dtype(dtype):
        pass

    @staticmethod
    def get_amp_supported_dtype():
        return [torch.float16]
    
    @staticmethod
    def _is_in_bad_fork():
        return False
    
    @staticmethod
    def manual_seed_all(seed: int) -> None:
        # We use the CPU Generator for the random number generation
        default_generator.manual_seed(seed)

    # Returns a copy of the given object in dml memory
    # Contiguous, one-dimensional array of elements of a
    # particular torch.dtype. It can be given any torch.dtype,
    # and the internal data will be interpreted appropriately.
    # torch.TypedStorage contains a torch.UntypedStorage which
    # holds the data as an untyped array of bytes.
    def _dml(self, dev=None, non_blocking=False, **kwargs):
        """Returns a copy of this object in dml memory.

            If this object is already in dml memory and on the correct device, then
            no copy is performed and the original object is returned.

            Args:
                dev (int): The destination GPU id. Defaults to the current device.
                non_blocking (bool): If ``True`` and the source is in pinned memory,
                    the copy will be asynchronous with respect to the host. Otherwise,
                    the argument has no effect.
        """
        non_blocking = torch._utils._get_async_or_non_blocking("privateuseone", non_blocking, kwargs)
        if dev is None:
            dml_device = device(default_device())
        else:
            dml_device = device(dev)

        with dml_device:
            if self.is_sparse:
                raise RuntimeError("UntypedStorage sparse copy is not supported.")
            else:
                untyped_storage = torch.UntypedStorage(self.size())
                untyped_storage.copy_(self, non_blocking)
                return untyped_storage

_StorageBase.privateuseone = PrivateUse1Module._dml
torch._register_device_module('privateuseone', PrivateUse1Module)
