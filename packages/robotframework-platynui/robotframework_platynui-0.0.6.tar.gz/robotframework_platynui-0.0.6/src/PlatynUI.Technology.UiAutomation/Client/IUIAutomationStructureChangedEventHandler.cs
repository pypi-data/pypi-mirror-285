using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[TypeLibType(TypeLibTypeFlags.FOleAutomation)]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("E81D1B4E-11C5-42F8-9754-E7036C79F054")]
[ComImport]
public interface IUIAutomationStructureChangedEventHandler
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void HandleStructureChangedEvent(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement sender,
        [In] StructureChangeType changeType,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId
    );
}
