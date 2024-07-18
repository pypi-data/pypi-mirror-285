using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("6A315D69-5512-4C2E-85F0-53FCE6DD4BC2")]
[ComImport]
public interface IUIAutomationTextRange3 : IUIAutomationTextRange2
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTextRange Clone();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int Compare([MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextRange range);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int CompareEndpoints(
        [In] TextPatternRangeEndpoint srcEndPoint,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextRange range,
        [In] TextPatternRangeEndpoint targetEndPoint
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void ExpandToEnclosingUnit([In] TextUnit TextUnit);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTextRange FindAttribute(
        [In] int attr,
        [MarshalAs(UnmanagedType.Struct), In] object val,
        [In] int backward
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationTextRange FindText(
        [MarshalAs(UnmanagedType.BStr), In] string text,
        [In] int backward,
        [In] int ignoreCase
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    new object GetAttributeValue([In] int attr);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_R8)]
    new double[] GetBoundingRectangles();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElement GetEnclosingElement();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    new string GetText([In] int maxLength);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int Move([In] TextUnit unit, [In] int count);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new int MoveEndpointByUnit([In] TextPatternRangeEndpoint endpoint, [In] TextUnit unit, [In] int count);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void MoveEndpointByRange(
        [In] TextPatternRangeEndpoint srcEndPoint,
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationTextRange range,
        [In] TextPatternRangeEndpoint targetEndPoint
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void Select();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void AddToSelection();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void RemoveFromSelection();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void ScrollIntoView([In] int alignToTop);

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    new IUIAutomationElementArray GetChildren();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    new void ShowContextMenu();

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElement GetEnclosingElementBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Interface)]
    IUIAutomationElementArray GetChildrenBuildCache(
        [MarshalAs(UnmanagedType.Interface), In] IUIAutomationCacheRequest cacheRequest
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_VARIANT)]
    object[] GetAttributeValues([In] ref int attributeIds, [In] int attributeIdCount);
}
