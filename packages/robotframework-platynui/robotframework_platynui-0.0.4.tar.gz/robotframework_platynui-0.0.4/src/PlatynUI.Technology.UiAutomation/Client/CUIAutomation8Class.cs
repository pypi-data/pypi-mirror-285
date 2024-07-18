using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[Guid("E22AD333-B25F-460C-83D0-0581107395C9")]
[TypeLibType(TypeLibTypeFlags.FCanCreate)]
[ClassInterface(ClassInterfaceType.None)]
[ComImport]
public class CUIAutomation8Class
    : IUIAutomation2,
        CUIAutomation8,
        IUIAutomation3,
        IUIAutomation4,
        IUIAutomation5,
        IUIAutomation6
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

    [DispId(1610743808)]
    public extern virtual int AutoSetFocus
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [DispId(1610743810)]
    public extern virtual uint ConnectionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [DispId(1610743812)]
    public extern virtual uint TransactionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation3_CompareElements(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation3_CompareRuntimeIds(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId1,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_GetRootElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_ElementFromHandle([In] IntPtr hwnd);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_ElementFromPoint([In] tagPOINT pt);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_GetFocusedElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_GetRootElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_ElementFromHandleBuildCache(
        [In] IntPtr hwnd,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_ElementFromPointBuildCache(
        [In] tagPOINT pt,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_GetFocusedElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationTreeWalker IUIAutomation3_CreateTreeWalker(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition pCondition
    );

    public extern virtual IUIAutomationTreeWalker IUIAutomation3_ControlViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation3_ContentViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation3_RawViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation3_RawViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation3_ControlViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation3_ContentViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCacheRequest IUIAutomation3_CreateCacheRequest();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateTrueCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateFalseCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreatePropertyCondition(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreatePropertyConditionEx(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value,
        [In] PropertyConditionFlags flags
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateAndCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateAndConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateAndConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateOrCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateOrConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateOrConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation3_CreateNotCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_AddAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_RemoveAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_AddPropertyChangedEventHandlerNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [In] ref int propertyArray,
        [In] int propertyCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_AddPropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] propertyArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_RemovePropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_AddStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_RemoveStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_AddFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_RemoveFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_RemoveAllEventHandlers();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)]
    public extern virtual int[] IUIAutomation3_IntNativeArrayToSafeArray([In] ref int array, [In] int arrayCount);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation3_IntSafeArrayToNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] intArray,
        [Out] IntPtr array
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    public extern virtual object IUIAutomation3_RectToVariant([In] tagRECT rc);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual tagRECT IUIAutomation3_VariantToRect([MarshalAs(UnmanagedType.Struct), In] object var);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation3_SafeArrayToRectNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_R8), In] double[] rects,
        [Out] IntPtr rectArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationProxyFactoryEntry IUIAutomation3_CreateProxyFactoryEntry(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationProxyFactory factory
    );

    public extern virtual IUIAutomationProxyFactoryMapping IUIAutomation3_ProxyFactoryMapping
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation3_GetPropertyProgrammaticName([In] int property);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation3_GetPatternProgrammaticName([In] int pattern);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_PollForPotentialSupportedPatterns(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] patternIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] patternNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation3_PollForPotentialSupportedProperties(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] propertyIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] propertyNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation3_CheckNotSupported([MarshalAs(UnmanagedType.Struct), In] object value);

    public extern virtual object IUIAutomation3_ReservedNotSupportedValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    public extern virtual object IUIAutomation3_ReservedMixedAttributeValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_ElementFromIAccessible(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation3_ElementFromIAccessibleBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    public extern virtual int IUIAutomation3_AutoSetFocus
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation3_ConnectionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation3_TransactionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] TextEditChangeType TextEditChangeType,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation4_CompareElements(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation4_CompareRuntimeIds(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId1,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_GetRootElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_ElementFromHandle([In] IntPtr hwnd);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_ElementFromPoint([In] tagPOINT pt);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_GetFocusedElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_GetRootElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_ElementFromHandleBuildCache(
        [In] IntPtr hwnd,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_ElementFromPointBuildCache(
        [In] tagPOINT pt,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_GetFocusedElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationTreeWalker IUIAutomation4_CreateTreeWalker(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition pCondition
    );

    public extern virtual IUIAutomationTreeWalker IUIAutomation4_ControlViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation4_ContentViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation4_RawViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation4_RawViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation4_ControlViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation4_ContentViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCacheRequest IUIAutomation4_CreateCacheRequest();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateTrueCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateFalseCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreatePropertyCondition(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreatePropertyConditionEx(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value,
        [In] PropertyConditionFlags flags
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateAndCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateAndConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateAndConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateOrCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateOrConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateOrConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation4_CreateNotCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_AddAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_RemoveAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_AddPropertyChangedEventHandlerNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [In] ref int propertyArray,
        [In] int propertyCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_AddPropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] propertyArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_RemovePropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_AddStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_RemoveStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_AddFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_RemoveFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_RemoveAllEventHandlers();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)]
    public extern virtual int[] IUIAutomation4_IntNativeArrayToSafeArray([In] ref int array, [In] int arrayCount);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation4_IntSafeArrayToNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] intArray,
        [Out] IntPtr array
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    public extern virtual object IUIAutomation4_RectToVariant([In] tagRECT rc);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual tagRECT IUIAutomation4_VariantToRect([MarshalAs(UnmanagedType.Struct), In] object var);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation4_SafeArrayToRectNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_R8), In] double[] rects,
        [Out] IntPtr rectArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationProxyFactoryEntry IUIAutomation4_CreateProxyFactoryEntry(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationProxyFactory factory
    );

    public extern virtual IUIAutomationProxyFactoryMapping IUIAutomation4_ProxyFactoryMapping
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation4_GetPropertyProgrammaticName([In] int property);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation4_GetPatternProgrammaticName([In] int pattern);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_PollForPotentialSupportedPatterns(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] patternIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] patternNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_PollForPotentialSupportedProperties(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] propertyIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] propertyNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation4_CheckNotSupported([MarshalAs(UnmanagedType.Struct), In] object value);

    public extern virtual object IUIAutomation4_ReservedNotSupportedValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    public extern virtual object IUIAutomation4_ReservedMixedAttributeValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_ElementFromIAccessible(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation4_ElementFromIAccessibleBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    public extern virtual int IUIAutomation4_AutoSetFocus
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation4_ConnectionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation4_TransactionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_AddTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] TextEditChangeType TextEditChangeType,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation4_RemoveTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] ref int changeTypes,
        [In] int changesCount,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest pCacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation5_CompareElements(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation5_CompareRuntimeIds(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId1,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_GetRootElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_ElementFromHandle([In] IntPtr hwnd);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_ElementFromPoint([In] tagPOINT pt);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_GetFocusedElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_GetRootElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_ElementFromHandleBuildCache(
        [In] IntPtr hwnd,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_ElementFromPointBuildCache(
        [In] tagPOINT pt,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_GetFocusedElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationTreeWalker IUIAutomation5_CreateTreeWalker(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition pCondition
    );

    public extern virtual IUIAutomationTreeWalker IUIAutomation5_ControlViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation5_ContentViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation5_RawViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation5_RawViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation5_ControlViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation5_ContentViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCacheRequest IUIAutomation5_CreateCacheRequest();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateTrueCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateFalseCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreatePropertyCondition(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreatePropertyConditionEx(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value,
        [In] PropertyConditionFlags flags
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateAndCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateAndConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateAndConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateOrCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateOrConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateOrConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation5_CreateNotCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_AddAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_RemoveAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_AddPropertyChangedEventHandlerNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [In] ref int propertyArray,
        [In] int propertyCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_AddPropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] propertyArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_RemovePropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_AddStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_RemoveStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_AddFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_RemoveFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_RemoveAllEventHandlers();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)]
    public extern virtual int[] IUIAutomation5_IntNativeArrayToSafeArray([In] ref int array, [In] int arrayCount);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation5_IntSafeArrayToNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] intArray,
        [Out] IntPtr array
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    public extern virtual object IUIAutomation5_RectToVariant([In] tagRECT rc);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual tagRECT IUIAutomation5_VariantToRect([MarshalAs(UnmanagedType.Struct), In] object var);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation5_SafeArrayToRectNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_R8), In] double[] rects,
        [Out] IntPtr rectArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationProxyFactoryEntry IUIAutomation5_CreateProxyFactoryEntry(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationProxyFactory factory
    );

    public extern virtual IUIAutomationProxyFactoryMapping IUIAutomation5_ProxyFactoryMapping
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation5_GetPropertyProgrammaticName([In] int property);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation5_GetPatternProgrammaticName([In] int pattern);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_PollForPotentialSupportedPatterns(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] patternIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] patternNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_PollForPotentialSupportedProperties(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] propertyIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] propertyNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation5_CheckNotSupported([MarshalAs(UnmanagedType.Struct), In] object value);

    public extern virtual object IUIAutomation5_ReservedNotSupportedValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    public extern virtual object IUIAutomation5_ReservedMixedAttributeValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_ElementFromIAccessible(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation5_ElementFromIAccessibleBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    public extern virtual int IUIAutomation5_AutoSetFocus
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation5_ConnectionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation5_TransactionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_AddTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] TextEditChangeType TextEditChangeType,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_RemoveTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_AddChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] ref int changeTypes,
        [In] int changesCount,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest pCacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation5_RemoveChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddNotificationEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationNotificationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveNotificationEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationNotificationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation6_CompareElements(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement el2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation6_CompareRuntimeIds(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId1,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] runtimeId2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_GetRootElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_ElementFromHandle([In] IntPtr hwnd);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_ElementFromPoint([In] tagPOINT pt);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_GetFocusedElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_GetRootElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_ElementFromHandleBuildCache(
        [In] IntPtr hwnd,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_ElementFromPointBuildCache(
        [In] tagPOINT pt,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_GetFocusedElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationTreeWalker IUIAutomation6_CreateTreeWalker(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition pCondition
    );

    public extern virtual IUIAutomationTreeWalker IUIAutomation6_ControlViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation6_ContentViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationTreeWalker IUIAutomation6_RawViewWalker
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation6_RawViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation6_ControlViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    public extern virtual IUIAutomationCondition IUIAutomation6_ContentViewCondition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCacheRequest IUIAutomation6_CreateCacheRequest();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateTrueCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateFalseCondition();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreatePropertyCondition(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreatePropertyConditionEx(
        [In] int propertyId,
        [MarshalAs(UnmanagedType.Struct), In] object value,
        [In] PropertyConditionFlags flags
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateAndCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateAndConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateAndConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateOrCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition1,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition2
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateOrConditionFromArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UNKNOWN), In]
            IUIAutomationCondition[] conditions
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateOrConditionFromNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] ref IUIAutomationCondition conditions,
        [In] int conditionCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationCondition IUIAutomation6_CreateNotCondition(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCondition condition
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemoveAutomationEventHandler(
        [In] int eventId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddPropertyChangedEventHandlerNativeArray(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [In] ref int propertyArray,
        [In] int propertyCount
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddPropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] propertyArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemovePropertyChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationPropertyChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemoveStructureChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationStructureChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemoveFocusChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationFocusChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemoveAllEventHandlers();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)]
    public extern virtual int[] IUIAutomation6_IntNativeArrayToSafeArray([In] ref int array, [In] int arrayCount);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation6_IntSafeArrayToNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT), In] int[] intArray,
        [Out] IntPtr array
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    public extern virtual object IUIAutomation6_RectToVariant([In] tagRECT rc);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual tagRECT IUIAutomation6_VariantToRect([MarshalAs(UnmanagedType.Struct), In] object var);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation6_SafeArrayToRectNativeArray(
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_R8), In] double[] rects,
        [Out] IntPtr rectArray
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationProxyFactoryEntry IUIAutomation6_CreateProxyFactoryEntry(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationProxyFactory factory
    );

    public extern virtual IUIAutomationProxyFactoryMapping IUIAutomation6_ProxyFactoryMapping
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation6_GetPropertyProgrammaticName([In] int property);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    public extern virtual string IUIAutomation6_GetPatternProgrammaticName([In] int pattern);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_PollForPotentialSupportedPatterns(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] patternIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] patternNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_PollForPotentialSupportedProperties(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement pElement,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_INT)] out int[] propertyIds,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_BSTR)] out string[] propertyNames
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual int IUIAutomation6_CheckNotSupported([MarshalAs(UnmanagedType.Struct), In] object value);

    public extern virtual object IUIAutomation6_ReservedNotSupportedValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    public extern virtual object IUIAutomation6_ReservedMixedAttributeValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.IUnknown)]
        get;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_ElementFromIAccessible(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    public extern virtual IUIAutomationElement IUIAutomation6_ElementFromIAccessibleBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IAccessible accessible,
        [In] int childId,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    public extern virtual int IUIAutomation6_AutoSetFocus
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation6_ConnectionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual uint IUIAutomation6_TransactionTimeout
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] TextEditChangeType TextEditChangeType,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemoveTextEditTextChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextEditTextChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [In] ref int changeTypes,
        [In] int changesCount,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest pCacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemoveChangesEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationChangesEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_AddNotificationEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationNotificationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void IUIAutomation6_RemoveNotificationEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationNotificationEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void CreateEventHandlerGroup(
        [MarshalAs(UnmanagedType.Interface)] out IUIAutomationEventHandlerGroup handlerGroup
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddEventHandlerGroup(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandlerGroup handlerGroup
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveEventHandlerGroup(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationEventHandlerGroup handlerGroup
    );

    public extern virtual ConnectionRecoveryBehaviorOptions ConnectionRecoveryBehavior
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    public extern virtual CoalesceEventsOptions CoalesceEvents
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void AddActiveTextPositionChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [In] TreeScope scope,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationActiveTextPositionChangedEventHandler handler
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    public extern virtual void RemoveActiveTextPositionChangedEventHandler(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement element,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationActiveTextPositionChangedEventHandler handler
    );
}
