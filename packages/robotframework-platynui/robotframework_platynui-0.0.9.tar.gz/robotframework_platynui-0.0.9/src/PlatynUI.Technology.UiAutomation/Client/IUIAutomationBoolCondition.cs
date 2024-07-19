using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("1B4E1F2E-75EB-4D0B-8952-5A69988E2307")]
[ComImport]
public interface IUIAutomationBoolCondition : IUIAutomationCondition
{
    [DispId(1610743808)]
    int BooleanValue
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        get;
    }
}
