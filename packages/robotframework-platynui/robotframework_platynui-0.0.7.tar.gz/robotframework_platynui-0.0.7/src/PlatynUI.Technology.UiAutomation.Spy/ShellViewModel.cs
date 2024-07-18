using System.Collections.ObjectModel;
using System.ComponentModel.Composition;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Input;
using System.Windows.Threading;
using Caliburn.Micro;
using PlatynUI.Technology.UiAutomation.Client;
using PlatynUI.Technology.UiAutomation.Core;
using PlatynUI.Technology.UiAutomation.Spy.ElementsModel;
using PlatynUI.Technology.UiAutomation.Tools;

namespace PlatynUI.Technology.UiAutomation.Spy;

[Export]
public sealed class ShellViewModel : Screen, IDisposable, IUIAutomationEventHandler
{
    private readonly Highlighter _highlighter = new(autoHideTimeout: 5000);
    private ElementBase _elements = new UiaRootElement();
    private ElementBase? _selectedElement;
    private string _title = "PlatynUI UiAutomation Spy";

    readonly DispatcherTimer dispatcherTimer = new();

    public ShellViewModel()
    {
        Automation.UiAutomation.AddAutomationEventHandler(
            UIA_EventIds.UIA_Window_WindowClosedEventId,
            Automation.RootElement,
            TreeScope.TreeScope_Children,
            null,
            this
        );
        Automation.UiAutomation.AddAutomationEventHandler(
            UIA_EventIds.UIA_Window_WindowOpenedEventId,
            Automation.RootElement,
            TreeScope.TreeScope_Children,
            null,
            this
        );

        dispatcherTimer.Tick += (sender, e) => OnTimerTick();
        dispatcherTimer.Interval = TimeSpan.FromSeconds(1);
        dispatcherTimer.Start();
    }

    public void Dispose()
    {
        Automation.UiAutomation.RemoveAllEventHandlers();
        _highlighter?.Dispose();
    }

    private void OnTimerTick()
    {
        if (Keyboard.IsKeyDown(Key.LeftCtrl) && Keyboard.IsKeyDown(Key.LeftShift))
        {
            Debug.WriteLine("Get element from point");
            var element = Automation.FromPoint(MouseDevice.GetPosition());

            if (element != null)
            {
                element = element.Realize();
                if (element.CurrentProcessId != UiAutomationElementExtensions.CurrentProcessId)
                {
                    var e = FindElement(element);
                    while (e == null)
                    {
                        element = element.GetCurrentParent();
                        if (element == null)
                        {
                            break;
                        }
                        e = FindElement(element);
                    }
                    if (e != null)
                        SelectElement(false, e);
                }
            }
        }
    }

    bool _topmost = false;

    public bool Topmost
    {
        get { return _topmost; }
        set
        {
            if (value == _topmost)
            {
                return;
            }

            _topmost = value;
            NotifyOfPropertyChange();
        }
    }

    public string Title
    {
        get => _title;
        set
        {
            if (value == _title)
            {
                return;
            }

            _title = value;
            NotifyOfPropertyChange();
        }
    }

    public ElementBase RootElement
    {
        get => _elements;
        set
        {
            if (Equals(value, _elements))
            {
                return;
            }

            _elements = value;
            NotifyOfPropertyChange();
        }
    }

    public ElementBase? SelectedElement
    {
        get => _selectedElement;
        set
        {
            if (Equals(value, _selectedElement))
            {
                return;
            }

            _selectedElement = value;
            NotifyOfPropertyChange();
        }
    }

    public void SetSelectedItem(ElementBase item)
    {
        try
        {
            SelectedElement = item;
            if (item is UiaElement uiaElement && uiaElement.AutomationElement.CurrentIsOffscreen == 0)
            {
                _highlighter.Show(uiaElement.AutomationElement.CurrentBoundingRectangle.ToRect());
            }
        }
        catch
        {
            // do nothing
        }
    }

    public async void Exit()
    {
        await TryCloseAsync();
    }

    public void RefreshElements()
    {
        if (SelectedElement == null)
        {
            SelectedElement = null;
            RootElement = new UiaRootElement();
        }
        else
        {
            SelectedElement.Refresh();
        }
    }

    public string XPath { get; set; } = string.Empty;

    public void ExecuteXPath(ActionExecutionContext context)
    {
        if (context.EventArgs is KeyEventArgs keyArgs && keyArgs.Key == Key.Enter)
        {
            SearchXPath(keyArgs.KeyboardDevice.Modifiers == ModifierKeys.Control);
        }
    }

    Cursor _cursor = Cursors.Arrow;
    public Cursor Cursor
    {
        get { return _cursor; }
        set
        {
            if (value == _cursor)
            {
                return;
            }

            _cursor = value;
            NotifyOfPropertyChange();
        }
    }

    ObservableCollection<FindResult> _results = [];

    public ObservableCollection<FindResult> Results
    {
        get { return _results; }
        set
        {
            if (Equals(value, _results))
            {
                return;
            }

            _results = value;
            NotifyOfPropertyChange();
        }
    }

    FindResult? _selectedFindResult = null;

    public FindResult? SelectedFindResult
    {
        get { return _selectedFindResult; }
        set
        {
            if (Equals(value, _selectedFindResult))
            {
                return;
            }
            _selectedFindResult = value;
            if (value != null)
            {
                SelectElement(false, value.Element);
            }
            NotifyOfPropertyChange();
        }
    }

    string _resultsCount = "";
    public string ResultsCount
    {
        get { return _resultsCount; }
        set
        {
            if (value == _resultsCount)
            {
                return;
            }
            _resultsCount = value;
            NotifyOfPropertyChange();
        }
    }

    string _lastErrorMessage = "";
    public string LastErrorMessage
    {
        get { return _lastErrorMessage; }
        set
        {
            if (value == _lastErrorMessage)
            {
                return;
            }
            _lastErrorMessage = value;
            NotifyOfPropertyChange();
        }
    }

    CancellationTokenSource? _searchCancellationTokenSource;

    public const string SEARCH_MODE_TEXT = "Search";
    public const string CANCEL_MODE_TEXT = "Cancel";

    string _searchMode = "Search";

    public string SearchMode
    {
        get { return _searchMode; }
        set
        {
            if (value == _searchMode)
            {
                return;
            }
            _searchMode = value;
            NotifyOfPropertyChange();
            NotifyOfPropertyChange("ProgressBarVisible");
        }
    }

    public Visibility ProgressBarVisible
    {
        get { return SearchMode == SEARCH_MODE_TEXT ? Visibility.Hidden : Visibility.Visible; }
    }

    public async void SearchXPath(bool focus = false)
    {
        if (_searchCancellationTokenSource != null)
        {
            _searchCancellationTokenSource.Cancel();
            _searchCancellationTokenSource = null;
            SearchMode = SEARCH_MODE_TEXT;
            return;
        }
        if (string.IsNullOrWhiteSpace(XPath))
        {
            return;
        }
        _searchCancellationTokenSource = new();
        var myCancellationTokenSource = _searchCancellationTokenSource;
        var token = _searchCancellationTokenSource.Token;
        try
        {
            LastErrorMessage = "";
            SearchMode = CANCEL_MODE_TEXT;

            var single = Keyboard.IsKeyDown(Key.LeftCtrl);

            await Task.Run(
                async () =>
                {
                    try
                    {
                        await Application.Current.Dispatcher.InvokeAsync(
                            () =>
                            {
                                Results.Clear();
                                ResultsCount = "";
                            },
                            DispatcherPriority.Normal,
                            token
                        );

                        IEnumerable<IUIAutomationElement> results = [];

                        if (single)
                        {
                            var element = Finder.FindSingleElement(null, XPath.Trim(), false);
                            if (element != null)
                            {
                                results = [element];
                            }
                        }
                        else
                        {
                            results = Finder.EnumAllElements(null, XPath.Trim(), false);
                        }

                        var first = true;
                        foreach (var element in results)
                        {
                            if (token.IsCancellationRequested)
                            {
                                break;
                            }
                            var e = FindElement(element);
                            if (e != null)
                            {
                                var result = new FindResult(e);

                                await Application.Current.Dispatcher.InvokeAsync(
                                    () =>
                                    {
                                        Results.Add(result);
                                        ResultsCount = $"{Results.Count} Elements";
                                    },
                                    DispatcherPriority.Normal,
                                    token
                                );
                                if (first)
                                {
                                    first = false;
                                    await Application.Current.Dispatcher.InvokeAsync(
                                        () =>
                                        {
                                            result.IsSelected = true;
                                            SelectElement(focus, result.Element);
                                        },
                                        DispatcherPriority.Normal,
                                        token
                                    );
                                }
                            }
                        }
                    }
                    catch (TaskCanceledException)
                    {
                        LastErrorMessage = "Canceled";
                    }
                    catch (Exception ex)
                    {
                        LastErrorMessage = $"{ex.GetType().Name}: {ex.Message}";
                    }
                },
                token
            );
        }
        finally
        {
            SearchMode = SEARCH_MODE_TEXT;
            _searchCancellationTokenSource = null;
            myCancellationTokenSource.Dispose();
            ResultsCount = $"{Results.Count} Elements";
        }
    }

    private ElementBase? FindElement(IUIAutomationElement element)
    {
        var parents = new List<IUIAutomationElement>();
        var parent = element.GetCurrentParent();

        if (parent != null)
        {
            while (parent != null)
            {
                parents.Insert(0, parent);
                parent = parent.GetCurrentParent();
            }

            //parents.Insert(0, (RootElement.Children.First() as UiaElement)!.AutomationElement);
        }
        var currentElement = RootElement;

        foreach (var parentElement in parents)
        {
            var foundElement = currentElement.FindAutomationElement(parentElement);

            if (foundElement == null)
            {
                break;
            }

            currentElement = foundElement;
        }

        if (currentElement != null)
        {
            return currentElement!.FindAutomationElement(element);
        }

        return currentElement;
    }

    private void SelectElement(bool focus, ElementBase element)
    {
        var parents = new List<ElementBase>();
        var parent = element.Parent;

        while (parent != null)
        {
            parents.Insert(0, parent);
            parent = parent.Parent;
        }

        parents.Insert(0, RootElement);

        foreach (var parentElement in parents)
        {
            parentElement.IsExpanded = true;
        }

        element.IsSelected = true;
    }

    public void HandleAutomationEvent(
        [In, MarshalAs(UnmanagedType.Interface)] IUIAutomationElement sender,
        [In] int eventId
    )
    {
        //_elements.Refresh();
        Debug.WriteLine($"HandleAutomationEvent: {sender.CurrentName} {eventId}");
    }
}
