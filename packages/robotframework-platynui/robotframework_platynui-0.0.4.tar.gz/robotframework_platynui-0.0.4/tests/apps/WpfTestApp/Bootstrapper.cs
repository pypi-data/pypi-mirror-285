using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.ComponentModel.Composition.Hosting;
using System.ComponentModel.Composition.ReflectionModel;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Windows;
using Caliburn.Micro;

namespace WpfTestApp;

public sealed class Bootstrapper : BootstrapperBase, IDisposable
{
    private static readonly ILog Logger;

    private CompositionContainer _container;

    static Bootstrapper()
    {
#if TRACE
        //Trace.Listeners.Add(new OutputWindowTraceListener("Trace Output"));
#endif

#if DEBUG
        LogManager.GetLog = type => new DebugLogger(type);
#endif
        Logger = LogManager.GetLog(typeof(Bootstrapper));
    }

    public Bootstrapper()
        : this(true) { }

    public Bootstrapper(bool useApplication)
        : base(useApplication)
    {
        Initialize();
    }

    public IEnumerable<string> ModuleDirectories
    {
        get
        {
            var exeDir = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
            if (string.IsNullOrEmpty(exeDir))
            {
                exeDir = ".";
            }

            return new[] { exeDir, Path.Combine(exeDir, "Internal"), Path.Combine(exeDir, "Modules") };
        }
    }

    public void Dispose()
    {
        if (_container != null)
        {
            _container.Dispose();
        }
    }

    protected override void Configure()
    {
        // Add all assemblies to AssemblySource (using a temporary DirectoryCatalog)

        foreach (var d in ModuleDirectories)
        {
            if (!Directory.Exists(d))
            {
                Logger.Info("Module directory '{0}' not exists, skipping", d);
                continue;
            }

            var directoryCatalog = new DirectoryCatalog(d);
            AssemblySource.Instance.AddRange(
                directoryCatalog
                    .Parts.Select(part => ReflectionModelServices.GetPartType(part).Value.Assembly)
                    .Where(assembly => !AssemblySource.Instance.Contains(assembly))
            );
        }

        // Prioritise the executable assembly. This allows the client project to override exports, including IShell.
        // The client project can override SelectAssemblies to choose which assemblies are prioritised.
        var priorityAssemblies = SelectAssemblies().ToList();
        var priorityCatalog = new AggregateCatalog(priorityAssemblies.Select(x => new AssemblyCatalog(x)));
        var priorityProvider = new CatalogExportProvider(priorityCatalog);

        // Now get all other assemblies (excluding the priority assemblies).
        var mainCatalog = new AggregateCatalog(
            AssemblySource
                .Instance.Where(assembly => !priorityAssemblies.Contains(assembly))
                .Select(x => new AssemblyCatalog(x))
        );
        var mainProvider = new CatalogExportProvider(mainCatalog);

        _container = new CompositionContainer(priorityProvider, mainProvider);
        priorityProvider.SourceProvider = _container;
        mainProvider.SourceProvider = _container;

        var batch = new CompositionBatch();

        BindServices(batch);

        batch.AddExportedValue(mainCatalog);

        _container.Compose(batch);
    }

    private void BindServices(CompositionBatch batch)
    {
        var windowManager = new WindowManager();
        batch.AddExportedValue<IWindowManager>(windowManager);

        batch.AddExportedValue<IEventAggregator>(new EventAggregator());
        batch.AddExportedValue(_container);
    }

    protected override object GetInstance(Type serviceType, string key)
    {
        // Skip trying to instantiate views since MEF will throw an exception
        if (typeof(UIElement).IsAssignableFrom(serviceType))
        {
            return null;
        }

        var contract = string.IsNullOrEmpty(key) ? AttributedModelServices.GetContractName(serviceType) : key;
        var exports = _container.GetExportedValues<object>(contract).ToList();

        if (exports.Any())
        {
            return exports.First();
        }

        throw new Exception($"Could not locate any instances of contract {contract}.");
    }

    protected override IEnumerable<object> GetAllInstances(Type serviceType)
    {
        return _container.GetExportedValues<object>(AttributedModelServices.GetContractName(serviceType));
    }

    protected override void BuildUp(object instance)
    {
        _container.SatisfyImportsOnce(instance);
    }

    protected override IEnumerable<Assembly> SelectAssemblies()
    {
        return [Assembly.GetEntryAssembly()];
    }

    protected override async void OnStartup(object sender, StartupEventArgs e)
    {
        await DisplayRootViewForAsync<ShellViewModel>();
    }
}
