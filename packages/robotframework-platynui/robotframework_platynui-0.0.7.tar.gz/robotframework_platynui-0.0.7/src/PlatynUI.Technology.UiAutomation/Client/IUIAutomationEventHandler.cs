using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[TypeLibType(TypeLibTypeFlags.FOleAutomation)]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("146C3C17-F12E-4E22-8C27-F894B9B79C69")]
[ComImport]
public interface IUIAutomationEventHandler
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void HandleAutomationEvent([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement sender, [In] int eventId);
}
