# PyD3XX
An unofficial Python wrapper for the FTDI D3XX library.  
PyD3XX supports Windows, Linux, and MacOS.  
All D3XX dynamic library variants are included in this package, so you don't need to include them directly in your project!  
\^You don't need and should not have any D3XX .dll, .dylib, or .so file in your script's directory.  
This was designed so the user needs zero ctypes knowledge and not need to import anything besides PyD3XX to interact with D3XX (FT600 & FT601) devices. The user should never have to interact with a ctypes object or method.  

## Plans
1. Fix segfault on program exit when on Linux or MacOS.  
2. Add a FT602 sub module in the future.  

## API - Classes
Here are the class equivalents for the D3XX structures and unique Python classes for this wrapper.

All D3XX Structure equivalents have variants of their variables with a "\_". These are usually a ctypes equivalent of the variable but are NOT directly used in the Python function calls except "\_Handle" in the FT\_Device class. YOU SHOULD IGNORE THE "_" variants unless you know what you're doing.

**All D3XX Structure equivalent classes have every variable accessible that the original structure has. The variables will have the same name as in the programming guide unless otherwise stated here.**

**If a class/structure's field/variable is not mentioned, it is an integer**.

### API - Classes - D3XX Structure Equivalents

**FT\_Device** == FT_DEVICE_LIST_INFO_NODE
> *FT\_Device should be passed into function calls and not FT\_Device.Handle or FT\_Device.\_Handle. Those just exist for your reference.*  
> Handle (int)  
> Flags (int)  
> Type (int)  
> ID (int)  
> LocID (int)  
> SerialNumber (str)  
> Description  (str)  

**FT\_DeviceDescriptor** == FT\_DEVICE\_DESCRIPTOR  
**FT\_ConfigurationDescriptor** == FT\_CONFIGURATION\_DESCRIPTOR  
**FT\_InterfaceDescriptor** == FT\_DEVICE\_DESCRIPTOR  
**FT\_StringDescriptor** == FT\_STRING\_DESCRIPTOR  
> szString (str)  

**FT\_Pipe** == FT\_PIPE\_INFORMATION  
**FT\_Overlapped** == OVERLAPPED  
**FT\_Pipe** == FT\_PIPE\_INFORMATION  
**FT\_SetupPacket** == FT\_SETUP\_PACKET  

**FT\_60XCONFIGURATION** == FT\_60XCONFIGURATION
> StringDescriptors (A list of str objects in the "utf_16_le" format).

### API - Classes - Python Specific
**FT_Buffer** | Used as a buffer for function calls.  
> from_int() - Creates an FT_Buffer from an integer.  
> from_str() - Creates an FT_Buffer from a string.  
> from_bytearray() - Creates an FT_Buffer from a bytearray.  
> from_bytes() - Creates an FT_Buffer from bytes.  
> Value() - Returns a bytearray of the FT_Buffer.  


## API - Functions

**FT_CreateDeviceInfoList() -> Status (int), DeviceCount (int):**

**FT_CreateDeviceInfoList() -> Status (int), DeviceCount (int):**

**FT_GetDeviceInfoList(DeviceCount: int) -> Status (int), DeviceList (list[FT_Device]):**

**FT_GetDeviceInfoDetail(Index: int) -> Status (int), Device (FT_Device):**

**FT_ListDevices(IndexCount: int, Flags: int) -> Status (int), Information (int  |  str  |  list[str]):**
> IndexCount = Index or Device Count

**FT_Create(Identifier, OpenFlag: int, Device: FT_Device) -> Status (int):**

**FT_Close(Device: FT_Device) -> Status (int):**

**FT_WritePipe(Device: FT_Device, Pipe: FT_Pipe, Buffer: FT_Buffer, BufferLength: int, Overlapped) -> Status (int), BytesTransferred(int):**
> Overlapped = FT_Overlapped or int(0) or NULL

**FT_WritePipeEx(Device: FT_Device, Pipe: FT_Pipe, Buffer: FT_Buffer, BufferLength: int, Overlapped) -> Status (int), BytesTransferred(int):**

**FT_ReadPipe(Device: FT_Device, Pipe: FT_Pipe, BufferLength: int, Overlapped) -> Status (int), Buffer (FT_Buffer), BytesTransferred (int):**

**FT_ReadPipeEx(Device: FT_Device, Pipe: FT_Pipe, BufferLength: int, Overlapped) -> Status (int), Buffer (FT_Buffer), BytesTransferred (int):**

**FT_GetOverlappedResult(Device: FT_Device, Overlapped: FT_Overlapped, Wait: bool) -> Status (int), LengthTransferred (int):**

**FT_InitializeOverlapped(Device: FT_Device) -> Status (int), Overlapped (FT_Overlapped):**
> Create an overlapped object.

**FT_ReleaseOverlapped(Device: FT_Device, Overlapped: FT_Overlapped) -> Status (int):**

**FT_SetStreamPipe(Device: FT_Device, AllWritePipes: bool, AllReadPipes: bool, Pipe: FT_Pipe  |  int, StreamSize: int) -> Status (int):**

**FT_ClearStreamPipe(Device: FT_Device, AllWritePipes: bool, AllReadPipes: bool, Pipe: FT_Pipe  |  int) -> Status (int):**

**FT_SetPipeTimeout(Device: FT_Device, Pipe: FT_Pipe, Timeout: int) -> Status (int):**

**FT_GetPipeTimeout(Device: FT_Device, Pipe: FT_Pipe) -> Status (int), Timeout (int):**

**FT_AbortPipe(Device: FT_Device, Pipe: FT_Pipe) -> Status (int):**

**FT_GetDeviceDescriptor(Device: FT_Device) -> Status (int), DeviceDescriptor (FT_DeviceDescriptor):**

**FT_GetConfigurationDescriptor(Device: FT_Device) -> Status (int),  ConfigurationDescriptor (FT_ConfigurationDescriptor):**

**FT_GetInterfaceDescriptor(Device: FT_Device, InterfaceIndex) -> Status (int),  InterfaceDescriptor (FT_InterfaceDescriptor):**

**FT_GetPipeInformation(Device: FT_Device, InterfaceIndex: int, PipeIndex: int) -> Status (int), Pipe (FT_Pipe):**

**FT_GetDescriptor(Device: FT_Device, DescriptorType: int, Index: int) -> Status (int), Descriptor (FT_DeviceDescriptor  |  FT_InterfaceDescriptor  |  FT_ConfigurationDescriptor  |  FT_StringDescriptor), LengthTransferred (int):**

**FT_ControlTransfer(Device: FT_Device, SetupPacket: FT_SetupPacket, Buffer: FT_Buffer, BufferLength: int) -> Status (int), LengthTransferred (int):**

**FT_GetVIDPID(Device: FT_Device) -> Status (int), VID (int), PID (int):**

**FT_EnableGPIO(Device: FT_Device, EnableMask: int, DirectionMask: int) -> Status (int):**

**FT_WriteGPIO(Device: FT_Device, SelectMask: int, Data: int) -> Status (int):**

**FT_ReadGPIO(Device: FT_Device) -> Status (int), GPIO_Data (int):**

**FT_SetGPIOPull(Device: FT_Device, SelectMask: int, PullMask: int) -> Status (int):**

**FT_SetNotificationCallback(Device: FT_Device, CallbackFunction: typing.Callable[[int, int, int], None]) -> Status (int):**

**FT_ClearNotificationCallback(Device: FT_Device) -> Status (int):**

**FT_GetChipConfiguration(Device: FT_Device) -> Status (int), Configuration (FT_60XCONFIGURATION):**

**FT_SetChipConfiguration(Device: FT_Device, Configuration: FT_60XCONFIGURATION) -> Status (int):**

**FT_IsDevicePath(Device: FT_Device, DevicePath: str) -> Status (int):**

**FT_GetDriverVersion(Device: FT_Device) -> Status (int), Version (int):**

**FT_GetLibraryVersion() -> Status (int), Version (int):**

**FT_CycleDevicePort(Device: FT_Device) -> Status (int):**

**FT_SetSuspendTimeout(Device: FT_Device, Timeout: int) -> Status (int):**

**FT_GetSuspendTimeout(Device: FT_Device) -> Status (int), Timeout (int):**

**FT_GetStringDescriptor(Device: FT_Device, StringIndex: int) -> Status (int), String Descriptor (FT_StringDescriptor):**

**FT_ReadPipeAsync(Device: FT_Device, FIFO_Index: int, BufferLength: int, Overlapped) -> Status (int), Buffer (FT_Buffer), BytesTransferred (int):**

**FT_WritePipeAsync(Device: FT_Device, FIFO_Index, Buffer: FT_Buffer, BufferLength: int, Overlapped) -> Status (int), BytesTransferred (int):**
