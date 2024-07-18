using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[Guid("85B94ECD-849D-42B6-B94D-D6DB23FDF5A4")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[ComImport]
public interface IUIAutomationProxyFactory
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IRawElementProviderSimple CreateProvider([In] IntPtr hwnd, [In] int idObject, [In] int idChild);

    [DispId(1610678273)]
    string ProxyFactoryId
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.BStr)]
        get;
    }
}
