using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[ClassInterface(ClassInterfaceType.None)]
[ComConversionLoss]
[Guid("FF48DBA4-60EF-4201-AA87-54103EEF594E")]
[TypeLibType(TypeLibTypeFlags.FCanCreate)]
[ComImport]
public class CUIAutomationClass : IUIAutomation, CUIAutomation
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int CompareElements(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int CompareRuntimeIds(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId1,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement GetRootElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement ElementFromHandle([In] IntPtr hwnd);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement ElementFromPoint([In] tagPOINT pt);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement GetFocusedElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement GetRootElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement ElementFromHandleBuildCache(
        [In] IntPtr hwnd,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement ElementFromPointBuildCache(
        [In] tagPOINT pt,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement GetFocusedElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationTreeWalker CreateTreeWalker(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition pCondition
    );

    [DispId(1610678283)]
    public extern virtual IUIAutomationTreeWalker ControlViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678284)]
    public extern virtual IUIAutomationTreeWalker ContentViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678285)]
    public extern virtual IUIAutomationTreeWalker RawViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678286)]
    public extern virtual IUIAutomationCondition RawViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678287)]
    public extern virtual IUIAutomationCondition ControlViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678288)]
    public extern virtual IUIAutomationCondition ContentViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCacheRequest CreateCacheRequest();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateTrueCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateFalseCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreatePropertyCondition(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreatePropertyConditionEx(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value,
        [In] PropertyConditionFlags flags
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateAndCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateAndConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateAndConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateOrCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateOrConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateOrConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition CreateNotCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddPropertyChangedEventHandlerNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [In] ref int propertyArray,
        [In] int propertyCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddPropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] propertyArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemovePropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveAllEventHandlers();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)]
    public extern virtual int[] IntNativeArrayToSafeArray([In] ref int array, [In] int arrayCount);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IntSafeArrayToNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] intArray,
        [Out] IntPtr array
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    public extern virtual object RectToVariant([In] tagRECT rc);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual tagRECT VariantToRect([MarshalAs(UnmanagedType.Struct), In] object var);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int SafeArrayToRectNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_R8), In] double[] rects,
        [Out] IntPtr rectArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationProxyFactoryEntry CreateProxyFactoryEntry(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationProxyFactory factory
    );

    [DispId(1610678317)]
    public extern virtual IUIAutomationProxyFactoryMapping ProxyFactoryMapping
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string GetPropertyProgrammaticName([In] int property);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string GetPatternProgrammaticName([In] int pattern);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void PollForPotentialSupportedPatterns(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] patternIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] patternNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void PollForPotentialSupportedProperties(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] propertyIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] propertyNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int CheckNotSupported([MarshalAs(UnmanagedType.Struct), In] object value);

    [DispId(1610678323)]
    public extern virtual object ReservedNotSupportedValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [DispId(1610678324)]
    public extern virtual object ReservedMixedAttributeValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement ElementFromIAccessible(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement ElementFromIAccessibleBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );
}
