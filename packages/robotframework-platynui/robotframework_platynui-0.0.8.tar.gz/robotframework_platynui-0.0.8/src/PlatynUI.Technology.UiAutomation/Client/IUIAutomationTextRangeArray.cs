using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("CE4AE76A-E717-4C98-81EA-47371D028EB6")]
[ComImport]
public interface IUIAutomationTextRangeArray
{
    [DispId(1610678272)]
    int Length
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationTextRange GetElement([In] int index);
}
