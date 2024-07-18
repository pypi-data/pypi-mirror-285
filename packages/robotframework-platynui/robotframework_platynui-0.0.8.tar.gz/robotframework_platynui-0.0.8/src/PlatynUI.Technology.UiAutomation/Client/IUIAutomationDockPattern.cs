using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("FDE5EF97-1464-48F6-90BF-43D0948E86EC")]
[ComImport]
public interface IUIAutomationDockPattern
{
    [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
    void SetDockPosition([In] DockPosition dockPos);

    [DispId(1610678273)]
    DockPosition CurrentDockPosition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
    }

    [DispId(1610678274)]
    DockPosition CachedDockPosition
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
    }
}
