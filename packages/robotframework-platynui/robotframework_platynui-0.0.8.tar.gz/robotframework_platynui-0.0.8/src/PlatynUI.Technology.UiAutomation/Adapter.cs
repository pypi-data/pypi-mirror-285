using System.Diagnostics;
using PlatynUI.Technology.UiAutomation.Client;
using PlatynUI.Technology.UiAutomation.Core;
using Windows.Win32;
using Windows.Win32.Foundation;
using Windows.Win32.UI.WindowsAndMessaging;

namespace PlatynUI.Technology.UiAutomation;

public static class Adapter
{
    public static string GetRole(IUIAutomationElement element)
    {
        if (element.GetCurrentParent() == null)
        {
            return "Desktop";
        }
        return element.GetCurrentControlTypeName();
    }

    public static string GetRuntimeId(IUIAutomationElement element)
    {
        return string.Join("-", element.GetRuntimeId().Select(id => id.ToString("X")));
    }

    public static bool IsReadOnly(IUIAutomationElement element)
    {
        if (element.TryGetCurrentPattern(out IUIAutomationValuePattern? pattern))
        {
            return pattern?.CurrentIsReadOnly != 0;
        }

        return false;
    }

    public static Point? GetClickablePoint(IUIAutomationElement element)
    {
        if (element.GetClickablePoint(out var tp) != 0)
        {
            return new Point(tp.x, tp.y);
        }

        var r = element.CurrentBoundingRectangle;
        return new Point(r.left + (r.right - r.left) / 2, r.top + (r.bottom - r.top) / 2);
    }

    public static IUIAutomationElement? GetTopLevelParent(IUIAutomationElement? element)
    {
        if (element == null)
        {
            return null;
        }

        var parent = Automation.RawViewWalker.GetParentElement(element);

        if (parent == null)
        {
            return null;
        }

        if (Automation.CompareElements(parent, Automation.RootElement))
        {
            return element;
        }

        return GetTopLevelParent(parent);
    }

    public static bool TryEnsureTopLevelParentIsActive(IUIAutomationElement? element)
    {
        if (element == null)
        {
            return false;
        }

        var topLevelParent = GetTopLevelParent(element);

        if (topLevelParent == null)
        {
            Console.WriteLine("Top level parent not found");
            return false;
        }

        var topLevelWindowHandle = topLevelParent.CurrentNativeWindowHandle;
        var foregroundWindowHandle = PInvoke.GetForegroundWindow();
        if (topLevelWindowHandle != IntPtr.Zero)
        {
            var topLevelElement = Automation.UiAutomation.ElementFromHandle(topLevelWindowHandle);
            if (topLevelElement.TryGetCurrentPattern<IUIAutomationWindowPattern>(out var pattern))
            {
                if (
                    pattern != null
                    && pattern.CurrentWindowInteractionState
                        == WindowInteractionState.WindowInteractionState_BlockedByModalWindow
                )
                {
                    return false;
                }
            }

            if (topLevelWindowHandle != foregroundWindowHandle)
            {
                var s = PInvoke.GetWindow(foregroundWindowHandle, GET_WINDOW_CMD.GW_OWNER);
                if (s == topLevelWindowHandle)
                {
                    var foregroundElement = Automation.UiAutomation.ElementFromHandle(foregroundWindowHandle);
                    if (foregroundElement.TryGetCurrentPattern<IUIAutomationWindowPattern>(out var pattern1))
                    {
                        if (pattern1 != null && pattern1.CurrentIsModal != 0)
                        {
                            return false;
                        }
                    }
                }

                PInvoke.SwitchToThisWindow((HWND)topLevelWindowHandle, false);

                Stopwatch sw = new();
                sw.Start();
                while (PInvoke.GetForegroundWindow() != topLevelWindowHandle && sw.ElapsedMilliseconds < 5000)
                {
                    Thread.Sleep(100);
                }

                return PInvoke.GetForegroundWindow() != topLevelWindowHandle;
            }
            else
            {
                return true;
            }
        }

        if (topLevelParent.CurrentIsKeyboardFocusable != 0 && topLevelParent.CurrentHasKeyboardFocus == 0)
        {
            topLevelParent.SetFocus();
            return true;
        }

        return false;
    }

    public static string[] GetSupportedPropertyNames(IUIAutomationElement element)
    {
        return Automation.GetSupportedPropertyNames(element);
    }

    public static object? GetPropertyValue(IUIAutomationElement element, string propertyName)
    {
        return Automation.GetPropertyValue(element, propertyName);
    }
}
