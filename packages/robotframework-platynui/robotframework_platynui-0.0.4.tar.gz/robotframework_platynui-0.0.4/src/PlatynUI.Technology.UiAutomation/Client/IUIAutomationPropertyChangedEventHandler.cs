using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client
{
    [Guid("40CD37D4-C756-4B0C-8C6F-BDDFEEB13B50")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    [TypeLibType(TypeLibTypeFlags.FOleAutomation)]
    [ComImport]
    public interface IUIAutomationPropertyChangedEventHandler
    {
        [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
        void HandlePropertyChangedEvent(
            [MarshalAs(UnmanagedType.Interface), In] IUIAutomationElement sender,
            [In] int propertyId,
            [MarshalAs(UnmanagedType.Struct), In] object newValue
        );
    }
}
