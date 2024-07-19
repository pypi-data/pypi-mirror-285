using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("4042C624-389C-4AFC-A630-9DF854A541FC")]
[ComImport]
public interface IUIAutomationTreeWalker
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetParentElement([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetFirstChildElement([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetLastChildElement([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetNextSiblingElement([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetPreviousSiblingElement(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement NormalizeElement([MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetParentElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetFirstChildElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetLastChildElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetNextSiblingElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetPreviousSiblingElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement NormalizeElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [DispId(1610678284)]
    IUIAutomationCondition condition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }
}
