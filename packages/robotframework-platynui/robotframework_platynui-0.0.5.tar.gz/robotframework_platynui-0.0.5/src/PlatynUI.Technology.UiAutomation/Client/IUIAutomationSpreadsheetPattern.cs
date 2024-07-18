using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("7517A7C8-FAAE-4DE9-9F08-29B91E8595C1")]
[ComImport]
public interface IUIAutomationSpreadsheetPattern
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetItemByName([MarshalAs(UnmanagedType.BStr), In] string name);
}
