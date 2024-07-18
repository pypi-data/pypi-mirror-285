using PlatynUI.Technology.UiAutomation.Tools;
using Windows.Win32;
using Windows.Win32.UI.WindowsAndMessaging;

namespace PlatynUI.Technology.UiAutomation;

public static class DisplayDevice
{
    public static Rect GetBoundingRectangle()
    {
        return new Rect(
            PInvoke.GetSystemMetrics(SYSTEM_METRICS_INDEX.SM_XVIRTUALSCREEN),
            PInvoke.GetSystemMetrics(SYSTEM_METRICS_INDEX.SM_YVIRTUALSCREEN),
            PInvoke.GetSystemMetrics(SYSTEM_METRICS_INDEX.SM_CXVIRTUALSCREEN),
            PInvoke.GetSystemMetrics(SYSTEM_METRICS_INDEX.SM_CYVIRTUALSCREEN)
        );
    }

    private static readonly Highlighter _highlighter = new(true);

    public static void HighlightRect(double x, double y, double width, double height, double time)
    {
        _highlighter.Show(new Rect(x, y, width, height), (int)time * 1000);
    }
}
