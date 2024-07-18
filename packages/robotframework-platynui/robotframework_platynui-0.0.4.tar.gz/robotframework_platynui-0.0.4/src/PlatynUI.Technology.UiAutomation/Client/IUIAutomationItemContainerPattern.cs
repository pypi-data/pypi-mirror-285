using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[Guid("C690FDB2-27A8-423C-812D-429773C9084E")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[ComImport]
public interface IUIAutomationItemContainerPattern
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement FindItemByProperty(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pStartAfter,
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value
    );
}
