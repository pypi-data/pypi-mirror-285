using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[Guid("C270F6B5-5C69-4290-9745-7A7F97169468")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[TypeLibType(TypeLibTypeFlags.FOleAutomation)]
[ComImport]
public interface IUIAutomationFocusChangedEventHandler
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void HandleFocusChangedEvent([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement sender);
}
