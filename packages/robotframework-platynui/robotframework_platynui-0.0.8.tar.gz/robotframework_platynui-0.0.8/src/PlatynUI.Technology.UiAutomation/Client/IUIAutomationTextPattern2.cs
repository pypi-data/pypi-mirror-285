using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("506A921A-FCC9-409F-B23B-37EB74106872")]
[ComImport]
public interface IUIAutomationTextPattern2 : IUIAutomationTextPattern
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTextRange RangeFromPoint([In] tagPOINT pt);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTextRange RangeFromChild([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement child);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTextRangeArray GetSelection();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTextRangeArray GetVisibleRanges();

    [DispId(1610678276)]
    new IUIAutomationTextRange DocumentRange
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678277)]
    new SupportedTextSelection SupportedTextSelection
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationTextRange RangeFromAnnotation(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement annotation
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationTextRange GetCaretRange(out int isActive);
}
