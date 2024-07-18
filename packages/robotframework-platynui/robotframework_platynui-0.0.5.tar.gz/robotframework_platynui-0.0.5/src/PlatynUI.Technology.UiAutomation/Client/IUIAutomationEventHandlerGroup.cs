using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("C9EE12F2-C13B-4408-997C-639914377F4E")]
[ComImport]
public interface IUIAutomationEventHandlerGroup
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddActiveTextPositionChangedEventHandler(
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationActiveTextPositionChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddAutomationEventHandler(
        [In] int eventId,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddChangesEventHandler(
        [In] TreeScope scope,
        [In] ref int changeTypes,
        [In] int changesCount,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddNotificationEventHandler(
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationNotificationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddPropertyChangedEventHandler(
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [In] ref int propertyArray,
        [In] int propertyCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddStructureChangedEventHandler(
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void AddTextEditTextChangedEventHandler(
        [In] TreeScope scope,
        [In] TextEditChangeType TextEditChangeType,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );
}
