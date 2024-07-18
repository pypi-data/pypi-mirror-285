using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[Guid("618736E0-3C3D-11CF-810C-00AA00389B71")]
[TypeLibType(TypeLibTypeFlags.FHidden | TypeLibTypeFlags.FDual | TypeLibTypeFlags.FDispatchable)]
[ComImport]
public interface IAccessible
{
    [DispId(-5000)]
    object accParent
    {
        [
            TypeLibFunc(TypeLibFuncFlags.FHidden),
            DispId(-5000),
            MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)
        ]
        [return: MarshalAs(UnmanagedType.IDispatch)]
        get;
    }

    [DispId(-5001)]
    int accChildCount
    {
        [
            TypeLibFunc(TypeLibFuncFlags.FHidden),
            DispId(-5001),
            MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)
        ]
        get;
    }

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5002)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.IDispatch)]
    object get_accChild([MarshalAs(UnmanagedType.Struct), In] object varChild);

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5003)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    string get_accName([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [DispId(-5004)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    string get_accValue([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5005)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    string get_accDescription([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5006)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    object get_accRole([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5007)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    object get_accState([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [DispId(-5008)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    string get_accHelp([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5009)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    int get_accHelpTopic(
        [MarshalAs(UnmanagedType.BStr)] out string pszHelpFile,
        [MarshalAs(UnmanagedType.Struct), In, Optional] object varChild
    );

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5010)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    string get_accKeyboardShortcut([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [DispId(-5011)]
    object accFocus
    {
        [
            DispId(-5011),
            TypeLibFunc(TypeLibFuncFlags.FHidden),
            MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)
        ]
        [return: MarshalAs(UnmanagedType.Struct)]
        get;
    }

    [DispId(-5012)]
    object accSelection
    {
        [
            DispId(-5012),
            TypeLibFunc(TypeLibFuncFlags.FHidden),
            MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)
        ]
        [return: MarshalAs(UnmanagedType.Struct)]
        get;
    }

    [DispId(-5013)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.BStr)]
    string get_accDefaultAction([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5014)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void accSelect([In] int flagsSelect, [MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [DispId(-5015)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void accLocation(
        out int pxLeft,
        out int pyTop,
        out int pcxWidth,
        out int pcyHeight,
        [MarshalAs(UnmanagedType.Struct), In, Optional] object varChild
    );

    [DispId(-5016)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    object accNavigate([In] int navDir, [MarshalAs(UnmanagedType.Struct), In, Optional] object varStart);

    [DispId(-5017)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    [return: MarshalAs(UnmanagedType.Struct)]
    object accHitTest([In] int xLeft, [In] int yTop);

    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [DispId(-5018)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void accDoDefaultAction([MarshalAs(UnmanagedType.Struct), In, Optional] object varChild);

    [DispId(-5003)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void set_accName(
        [MarshalAs(UnmanagedType.Struct), In, Optional] object varChild,
        [MarshalAs(UnmanagedType.BStr), In] string pszName
    );

    [DispId(-5004)]
    [TypeLibFunc(TypeLibFuncFlags.FHidden)]
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void set_accValue(
        [MarshalAs(UnmanagedType.Struct), In, Optional] object varChild,
        [MarshalAs(UnmanagedType.BStr), In] string pszValue
    );
}
