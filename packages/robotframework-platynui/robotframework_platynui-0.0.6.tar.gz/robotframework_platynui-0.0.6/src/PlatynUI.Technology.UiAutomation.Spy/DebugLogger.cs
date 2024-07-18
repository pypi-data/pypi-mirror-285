using System.Diagnostics;
using Caliburn.Micro;

namespace PlatynUI.Technology.UiAutomation.Spy;

public class DebugLogger : ILog
{
    private readonly Type _type;

    public DebugLogger(Type type)
    {
        _type = type;
    }

    public void Info(string format, params object[] args)
    {
        Debug.WriteLine($"INFO [{_type}]: {string.Format(format, args)}");
    }

    public void Warn(string format, params object[] args)
    {
        Debug.WriteLine($"WARN [{_type}]: {string.Format(format, args)}");
    }

    public void Error(Exception exception)
    {
        Debug.WriteLine($"ERROR [{_type}]: {exception}");
    }
}
