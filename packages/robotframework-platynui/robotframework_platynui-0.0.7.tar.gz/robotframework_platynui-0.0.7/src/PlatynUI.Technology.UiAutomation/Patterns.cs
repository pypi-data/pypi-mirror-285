using PlatynUI.Technology.UiAutomation.Client;
using PlatynUI.Technology.UiAutomation.Core;
using Windows.Win32;
using Windows.Win32.Foundation;
using Windows.Win32.UI.WindowsAndMessaging;

namespace PlatynUI.Technology.UiAutomation;

public static class Patterns
{
    public class WindowPattern(IUIAutomationElement element, IUIAutomationWindowPattern pattern)
    {
        private readonly IUIAutomationElement element = element;
        private readonly IUIAutomationWindowPattern pattern = pattern;

        public bool CanMinimize => pattern.CurrentCanMinimize != 0;
        public bool IsMinimized => pattern.CurrentWindowVisualState == WindowVisualState.WindowVisualState_Minimized;

        public void Minimize() => pattern.SetWindowVisualState(WindowVisualState.WindowVisualState_Minimized);

        public bool CanMaximize => pattern.CurrentCanMaximize != 0;
        public bool IsMaximized => pattern.CurrentWindowVisualState == WindowVisualState.WindowVisualState_Maximized;

        public void Maximize() => pattern.SetWindowVisualState(WindowVisualState.WindowVisualState_Maximized);

        public void Restore() => pattern.SetWindowVisualState(WindowVisualState.WindowVisualState_Normal);

        public void Close() => pattern.Close();

        public bool IsActive
        {
            get
            {
                var h = element.CurrentNativeWindowHandle;
                if (h != IntPtr.Zero)
                {
                    return h == PInvoke.GetForegroundWindow();
                }

                return element.CurrentIsKeyboardFocusable != 0 && element.CurrentHasKeyboardFocus == 0;
            }
        }

        public virtual void Activate()
        {
            if (IsActive)
            {
                return;
            }

            if (IsMinimized)
            {
                Restore();
            }

            var h = element.CurrentNativeWindowHandle;
            if (h != IntPtr.Zero)
            {
                var element = Automation.ElementFromHandle(h);
                if (element.TryGetCurrentPattern<IUIAutomationWindowPattern>(out var pattern))
                {
                    if (
                        pattern?.CurrentWindowInteractionState
                        == WindowInteractionState.WindowInteractionState_BlockedByModalWindow
                    )
                    {
                        return;
                    }
                }

                var foregroundWindow = PInvoke.GetForegroundWindow();
                if (h != foregroundWindow)
                {
                    var s = PInvoke.GetWindow(foregroundWindow, GET_WINDOW_CMD.GW_OWNER);
                    if (s == h)
                    {
                        var foregroundElement = Automation.ElementFromHandle(foregroundWindow);
                        if (foregroundElement.TryGetCurrentPattern<IUIAutomationWindowPattern>(out var pattern1))
                        {
                            if (pattern1?.CurrentIsModal != 0)
                            {
                                return;
                            }
                        }
                    }

                    PInvoke.SwitchToThisWindow((HWND)h, false);
                    return;
                }
            }

            if (element.CurrentIsKeyboardFocusable != 0 && element.CurrentHasKeyboardFocus == 0)
            {
                element.SetFocus();
                return;
            }

            throw new NotSupportedException("Don't know how to activate this");
        }
    }

    public static WindowPattern? GetWindowPattern(IUIAutomationElement element)
    {
        if (element.TryGetCurrentPattern(out IUIAutomationWindowPattern? pattern))
        {
            if (pattern != null)
            {
                return new WindowPattern(element, pattern);
            }
        }
        return null;
    }

    public class NativeWindowPattern(IUIAutomationElement element)
    {
        public IUIAutomationElement Element { get; } = element;

        public bool IsActive
        {
            get
            {
                var h = Element.CurrentNativeWindowHandle;
                if (h != IntPtr.Zero)
                {
                    return h == PInvoke.GetForegroundWindow();
                }

                return Element.CurrentIsKeyboardFocusable != 0 && Element.CurrentHasKeyboardFocus == 0;
            }
        }

        public virtual void Activate()
        {
            if (IsActive)
            {
                return;
            }

            var h = Element.CurrentNativeWindowHandle;
            if (h != IntPtr.Zero)
            {
                var foregroundWindow = PInvoke.GetForegroundWindow();
                if (h != foregroundWindow)
                {
                    var s = PInvoke.GetWindow(foregroundWindow, GET_WINDOW_CMD.GW_OWNER);
                    if (s == h)
                    {
                        var foregroundElement = Automation.ElementFromHandle(foregroundWindow);
                        if (foregroundElement.TryGetCurrentPattern<IUIAutomationWindowPattern>(out var pattern1))
                        {
                            if (pattern1?.CurrentIsModal != 0)
                            {
                                return;
                            }
                        }
                    }

                    PInvoke.SwitchToThisWindow((HWND)h, false);
                    return;
                }
            }

            if (Element.CurrentIsKeyboardFocusable != 0 && Element.CurrentHasKeyboardFocus == 0)
            {
                Element.SetFocus();
                return;
            }

            throw new NotSupportedException("Don't know how to activate this");
        }
    }

    public static NativeWindowPattern GetNativeWindowPattern(IUIAutomationElement element)
    {
        if (element.CurrentNativeWindowHandle != IntPtr.Zero)
        {
            return new NativeWindowPattern(element);
        }

        throw new NotSupportedException();
    }
}
