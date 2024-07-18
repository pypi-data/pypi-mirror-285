using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using PlatynUI.Technology.UiAutomation.Client;

namespace PlatynUI.Technology.UiAutomation.Core;

public class Automation
{
    public readonly struct PropertyIdAndName(int id, string name)
    {
        public readonly int Id = id;
        public readonly string Name = name;
    }

    public static IUIAutomation UiAutomation { get; } = new CUIAutomation();

    public static IUIAutomationElement RootElement => UiAutomation.GetRootElement();

    public static IUIAutomationElement GetCachedRootElement()
    {
        var request = UiAutomation.CreateCacheRequest();
        request.AutomationElementMode = AutomationElementMode.AutomationElementMode_Full;
        request.TreeScope = TreeScope.TreeScope_Subtree;
        request.TreeFilter = UiAutomation.CreateTrueCondition();
        return UiAutomation.GetRootElementBuildCache(request);
    }

    public static IUIAutomationElement? FromPoint(Point point)
    {
        try
        {
            return UiAutomation.ElementFromPoint(new tagPOINT { x = (int)point.X, y = (int)point.Y });
        }
        catch (Exception e)
        {
            Debug.WriteLine($"Failed to get element from point {point.X}, {point.Y}: {e.Message}");
        }
        return null;
    }

    public static object NotSupportedValue => UiAutomation.ReservedNotSupportedValue;

    public static bool CompareElements(IUIAutomationElement? e1, IUIAutomationElement? e2)
    {
        if (e1 == null || e2 == null)
        {
            return false;
        }

        try
        {
            return UiAutomation.CompareElements(e1, e2) != 0;
        }
        catch (Exception e)
        {
            Debug.WriteLine($"Failed to compare elements: {e.Message}");
            return false;
        }
    }

    private static string GetTypeGuid(MemberInfo type)
    {
        var attr = type.GetCustomAttribute<GuidAttribute>();
        if (attr == null)
        {
            return "<invalid>";
        }

        return attr.Value;
    }

    private static readonly Dictionary<string, int> KnownPatternIds =
        new()
        {
            { GetTypeGuid(typeof(IUIAutomationInvokePattern)), UIA_PatternIds.UIA_InvokePatternId },
            { GetTypeGuid(typeof(IUIAutomationSelectionPattern)), UIA_PatternIds.UIA_SelectionPatternId },
            { GetTypeGuid(typeof(IUIAutomationValuePattern)), UIA_PatternIds.UIA_ValuePatternId },
            { GetTypeGuid(typeof(IUIAutomationRangeValuePattern)), UIA_PatternIds.UIA_RangeValuePatternId },
            { GetTypeGuid(typeof(IUIAutomationScrollPattern)), UIA_PatternIds.UIA_ScrollPatternId },
            { GetTypeGuid(typeof(IUIAutomationExpandCollapsePattern)), UIA_PatternIds.UIA_ExpandCollapsePatternId },
            { GetTypeGuid(typeof(IUIAutomationGridPattern)), UIA_PatternIds.UIA_GridPatternId },
            { GetTypeGuid(typeof(IUIAutomationGridItemPattern)), UIA_PatternIds.UIA_GridItemPatternId },
            { GetTypeGuid(typeof(IUIAutomationMultipleViewPattern)), UIA_PatternIds.UIA_MultipleViewPatternId },
            { GetTypeGuid(typeof(IUIAutomationWindowPattern)), UIA_PatternIds.UIA_WindowPatternId },
            { GetTypeGuid(typeof(IUIAutomationSelectionItemPattern)), UIA_PatternIds.UIA_SelectionItemPatternId },
            { GetTypeGuid(typeof(IUIAutomationDockPattern)), UIA_PatternIds.UIA_DockPatternId },
            { GetTypeGuid(typeof(IUIAutomationTablePattern)), UIA_PatternIds.UIA_TablePatternId },
            { GetTypeGuid(typeof(IUIAutomationTableItemPattern)), UIA_PatternIds.UIA_TableItemPatternId },
            { GetTypeGuid(typeof(IUIAutomationTextPattern)), UIA_PatternIds.UIA_TextPatternId },
            { GetTypeGuid(typeof(IUIAutomationTogglePattern)), UIA_PatternIds.UIA_TogglePatternId },
            { GetTypeGuid(typeof(IUIAutomationTransformPattern)), UIA_PatternIds.UIA_TransformPatternId },
            { GetTypeGuid(typeof(IUIAutomationScrollItemPattern)), UIA_PatternIds.UIA_ScrollItemPatternId },
            {
                GetTypeGuid(typeof(IUIAutomationLegacyIAccessiblePattern)),
                UIA_PatternIds.UIA_LegacyIAccessiblePatternId
            },
            { GetTypeGuid(typeof(IUIAutomationItemContainerPattern)), UIA_PatternIds.UIA_ItemContainerPatternId },
            { GetTypeGuid(typeof(IUIAutomationVirtualizedItemPattern)), UIA_PatternIds.UIA_VirtualizedItemPatternId },
            {
                GetTypeGuid(typeof(IUIAutomationSynchronizedInputPattern)),
                UIA_PatternIds.UIA_SynchronizedInputPatternId
            },
            { GetTypeGuid(typeof(IUIAutomationObjectModelPattern)), UIA_PatternIds.UIA_ObjectModelPatternId },
            { GetTypeGuid(typeof(IUIAutomationAnnotationPattern)), UIA_PatternIds.UIA_AnnotationPatternId },
            { GetTypeGuid(typeof(IUIAutomationTextPattern2)), UIA_PatternIds.UIA_TextPattern2Id },
            { GetTypeGuid(typeof(IUIAutomationStylesPattern)), UIA_PatternIds.UIA_StylesPatternId },
            { GetTypeGuid(typeof(IUIAutomationSpreadsheetPattern)), UIA_PatternIds.UIA_SpreadsheetPatternId },
            { GetTypeGuid(typeof(IUIAutomationSpreadsheetItemPattern)), UIA_PatternIds.UIA_SpreadsheetItemPatternId },
            { GetTypeGuid(typeof(IUIAutomationTransformPattern2)), UIA_PatternIds.UIA_TransformPattern2Id },
            { GetTypeGuid(typeof(IUIAutomationTextChildPattern)), UIA_PatternIds.UIA_TextChildPatternId },
            { GetTypeGuid(typeof(IUIAutomationDragPattern)), UIA_PatternIds.UIA_DragPatternId },
            { GetTypeGuid(typeof(IUIAutomationDropTargetPattern)), UIA_PatternIds.UIA_DropTargetPatternId },
            { GetTypeGuid(typeof(IUIAutomationTextEditPattern)), UIA_PatternIds.UIA_TextEditPatternId }
        };

    public static bool TryGetCurrentPattern<T>(IUIAutomationElement element, out T? pattern)
        where T : class
    {
        pattern = default;

        if (!KnownPatternIds.TryGetValue(GetTypeGuid(typeof(T)), out var id) || !SupportsPatternId(element, id))
        {
            return false;
        }

        pattern = element.GetCurrentPattern(id) as T;
        return pattern != null;
    }

    public static int[] GetSupportedPatternIds(IUIAutomationElement element)
    {
        UiAutomation.PollForPotentialSupportedPatterns(element, out var ids, out _);

        return ids;
    }

    public static bool SupportsPatternId(IUIAutomationElement element, int id)
    {
        return GetSupportedPatternIds(element).Contains(id);
    }

    public static PropertyIdAndName[] GetSupportedPropertyIdAndNames(IUIAutomationElement element)
    {
        UiAutomation.PollForPotentialSupportedProperties(element, out var ids, out var names);
        if (ids == null || names == null)
        {
            return [];
        }

        return ids.Select((t, i) => new PropertyIdAndName(t, names[i])).Where(n => n.Id > 0).ToArray();
    }

    public static IUIAutomationTreeWalker RawViewWalker => UiAutomation.RawViewWalker;
    public static IUIAutomationTreeWalker ContentViewWalker => UiAutomation.ContentViewWalker;
    public static IUIAutomationTreeWalker ControlViewWalker => UiAutomation.ControlViewWalker;

    public static T? GetCurrentPattern<T>(IUIAutomationElement element)
        where T : class
    {
        if (TryGetCurrentPattern(element, out T? pattern))
        {
            return pattern;
        }

        throw new NotSupportedException($"Element does not support pattern {typeof(T)}");
    }

    public static bool TryGetCachedPattern<T>(IUIAutomationElement element, out T? pattern)
        where T : class
    {
        pattern = default;

        if (!KnownPatternIds.TryGetValue(GetTypeGuid(typeof(T)), out var id) || !SupportsPatternId(element, id))
        {
            return false;
        }

        pattern = element.GetCachedPattern(id) as T;
        return pattern != null;
    }

    public static T? GetCachedPattern<T>(IUIAutomationElement element)
        where T : class
    {
        if (TryGetCachedPattern(element, out T? pattern))
        {
            return pattern;
        }

        throw new NotSupportedException($"Element does not support cached pattern {typeof(T)}");
    }

    public static bool SupportsPattern<T>(IUIAutomationElement element)
        where T : class
    {
        try
        {
            return KnownPatternIds.TryGetValue(GetTypeGuid(typeof(T)), out var id) && SupportsPatternId(element, id);
        }
        catch
        {
            return false;
        }
    }

    public static string[] GetSupportedPatternNames(IUIAutomationElement element)
    {
        UiAutomation.PollForPotentialSupportedPatterns(element, out _, out var names);

        return names;
    }

    private static readonly Dictionary<int, string> KnownControlTypes =
        new()
        {
            { UIA_ControlTypeIds.UIA_ButtonControlTypeId, "Button" },
            { UIA_ControlTypeIds.UIA_CalendarControlTypeId, "Calendar" },
            { UIA_ControlTypeIds.UIA_CheckBoxControlTypeId, "CheckBox" },
            { UIA_ControlTypeIds.UIA_ComboBoxControlTypeId, "ComboBox" },
            { UIA_ControlTypeIds.UIA_EditControlTypeId, "Edit" },
            { UIA_ControlTypeIds.UIA_HyperlinkControlTypeId, "Hyperlink" },
            { UIA_ControlTypeIds.UIA_ImageControlTypeId, "Image" },
            { UIA_ControlTypeIds.UIA_ListItemControlTypeId, "ListItem" },
            { UIA_ControlTypeIds.UIA_ListControlTypeId, "List" },
            { UIA_ControlTypeIds.UIA_MenuControlTypeId, "Menu" },
            { UIA_ControlTypeIds.UIA_MenuBarControlTypeId, "MenuBar" },
            { UIA_ControlTypeIds.UIA_MenuItemControlTypeId, "MenuItem" },
            { UIA_ControlTypeIds.UIA_ProgressBarControlTypeId, "ProgressBar" },
            { UIA_ControlTypeIds.UIA_RadioButtonControlTypeId, "RadioButton" },
            { UIA_ControlTypeIds.UIA_ScrollBarControlTypeId, "ScrollBar" },
            { UIA_ControlTypeIds.UIA_SliderControlTypeId, "Slider" },
            { UIA_ControlTypeIds.UIA_SpinnerControlTypeId, "Spinner" },
            { UIA_ControlTypeIds.UIA_StatusBarControlTypeId, "StatusBar" },
            { UIA_ControlTypeIds.UIA_TabControlTypeId, "Tab" },
            { UIA_ControlTypeIds.UIA_TabItemControlTypeId, "TabItem" },
            { UIA_ControlTypeIds.UIA_TextControlTypeId, "Text" },
            { UIA_ControlTypeIds.UIA_ToolBarControlTypeId, "ToolBar" },
            { UIA_ControlTypeIds.UIA_ToolTipControlTypeId, "ToolTip" },
            { UIA_ControlTypeIds.UIA_TreeControlTypeId, "Tree" },
            { UIA_ControlTypeIds.UIA_TreeItemControlTypeId, "TreeItem" },
            { UIA_ControlTypeIds.UIA_CustomControlTypeId, "Custom" },
            { UIA_ControlTypeIds.UIA_GroupControlTypeId, "Group" },
            { UIA_ControlTypeIds.UIA_ThumbControlTypeId, "Thumb" },
            { UIA_ControlTypeIds.UIA_DataGridControlTypeId, "DataGrid" },
            { UIA_ControlTypeIds.UIA_DataItemControlTypeId, "DataItem" },
            { UIA_ControlTypeIds.UIA_DocumentControlTypeId, "Document" },
            { UIA_ControlTypeIds.UIA_SplitButtonControlTypeId, "SplitButton" },
            { UIA_ControlTypeIds.UIA_WindowControlTypeId, "Window" },
            { UIA_ControlTypeIds.UIA_PaneControlTypeId, "Pane" },
            { UIA_ControlTypeIds.UIA_HeaderControlTypeId, "Header" },
            { UIA_ControlTypeIds.UIA_HeaderItemControlTypeId, "HeaderItem" },
            { UIA_ControlTypeIds.UIA_TableControlTypeId, "Table" },
            { UIA_ControlTypeIds.UIA_TitleBarControlTypeId, "TitleBar" },
            { UIA_ControlTypeIds.UIA_SeparatorControlTypeId, "Separator" },
            { UIA_ControlTypeIds.UIA_SemanticZoomControlTypeId, "SemanticZoom" },
            { UIA_ControlTypeIds.UIA_AppBarControlTypeId, "AppBar" }
        };

    public static string ControlTypeNameFromId(int id)
    {
        return KnownControlTypes.TryGetValue(id, out var result) ? result : "*";
    }

    public static int[] GetSupportedPropertyIds(IUIAutomationElement element)
    {
        UiAutomation.PollForPotentialSupportedProperties(element, out var ids, out _);

        return ids;
    }

    public static string[] GetSupportedPropertyNames(IUIAutomationElement element)
    {
        UiAutomation.PollForPotentialSupportedProperties(element, out _, out var names);

        return [.. names.Append("Role").OrderBy(name => name)];
    }

    public static object? GetPropertyValue(IUIAutomationElement element, string propertyName)
    {
        if (propertyName == "Role")
        {
            return element.GetCurrentControlTypeName();
        }

        UiAutomation.PollForPotentialSupportedProperties(element, out var ids, out var names);

        var index = Array.IndexOf(names, propertyName);
        if (index < 0)
        {
            throw new NotSupportedException($"Property {propertyName} is not supported");
        }
        var v = element.GetCurrentPropertyValueEx(ids[index], 0);

        return ConvertPropertyValue(propertyName, v);
    }

    public static object? ConvertPropertyValue(string name, object value)
    {
        if (UiAutomation.CheckNotSupported(value) != 0)
        {
            return null;
        }

        switch (name)
        {
            case "RuntimeId":
                return string.Join("-", ((int[])value).Select(id => id.ToString("X")));
            case "BoundingRectangle":
                if (value is double[] rect)
                {
                    return $"({rect[0]}, {rect[1]}) - ({rect[2]}, {rect[3]})";
                }
                break;
            case "ClickablePoint":
                if (value is double[] point)
                {
                    return $"({point[0]}, {point[1]})";
                }
                break;
        }
        return value switch
        {
            int[] array => string.Join(", ", array),
            double[] array => string.Join(", ", array),
            string[] array => string.Join(", ", array),
            _ => value,
        };
    }

    public static IUIAutomationElement ElementFromHandle(IntPtr handle)
    {
        return UiAutomation.ElementFromHandle(handle);
    }
}
