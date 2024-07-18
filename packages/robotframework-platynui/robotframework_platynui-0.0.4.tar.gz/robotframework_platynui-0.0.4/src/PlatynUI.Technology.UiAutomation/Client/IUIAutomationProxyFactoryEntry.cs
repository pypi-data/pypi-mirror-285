using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("D50E472E-B64B-490C-BCA1-D30696F9F289")]
[ComImport]
public interface IUIAutomationProxyFactoryEntry
{
    [DispId(1610678272)]
    IUIAutomationProxyFactory ProxyFactory
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.Interface)]
        get;
    }

    [DispId(1610678273)]
    string ClassName
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.BStr)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: MarshalAs(UnmanagedType.LPWStr), In]
        set;
    }

    [DispId(1610678274)]
    string ImageName
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [return: MarshalAs(UnmanagedType.BStr)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: MarshalAs(UnmanagedType.LPWStr), In]
        set;
    }

    [DispId(1610678275)]
    int AllowSubstringMatch
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [DispId(1610678276)]
    int CanCheckBaseClass
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [DispId(1610678277)]
    int NeedsAdviseEvents
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        [param: In]
        set;
    }

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void SetWinEventsForAutomationEvent(
        [In] int eventId,
        [In] int propertyId,
        [MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UINT), In] uint[] winEvents
    );

    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_UINT)]
    uint[] GetWinEventsForAutomationEvent([In] int eventId, [In] int propertyId);
}
