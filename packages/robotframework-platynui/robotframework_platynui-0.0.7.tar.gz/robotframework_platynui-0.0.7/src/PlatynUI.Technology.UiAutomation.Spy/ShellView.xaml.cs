using System.Collections.ObjectModel;
using System.Windows;
using System.Windows.Controls;

namespace PlatynUI.Technology.UiAutomation.Spy;

public partial class ShellView
{
    public ShellView()
    {
        InitializeComponent();
    }

    private void TreeViewSelectedItemChanged(object sender, RoutedEventArgs e)
    {
        if (sender is TreeViewItem item)
        {
            item.BringIntoView();
            e.Handled = true;
        }
    }
}
