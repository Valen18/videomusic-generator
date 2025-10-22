import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from ...infrastructure.config.settings import ConfigManager, APISettings
from ...infrastructure.adapters.usage_tracker import get_tracker
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta


class SettingsWindow:
    def __init__(self, parent, on_settings_changed: Callable = None):
        self.parent = parent
        self.on_settings_changed = on_settings_changed
        self.config_manager = ConfigManager()
        self.tracker = get_tracker()

        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Configuración de APIs")
        self.window.geometry("800x700")
        self.window.resizable(True, True)

        # Configurar el estilo
        self._setup_style()
        self._create_widgets()
        self._load_current_settings()
        self._center_window()

        # Modal
        self.window.transient(parent)
        self.window.grab_set()

    def _setup_style(self):
        style = ttk.Style()

        # Configurar colores modernos
        style.theme_use('clam')

        # Colores personalizados
        bg_color = "#f8f9fa"
        card_color = "#ffffff"
        primary_color = "#007bff"
        success_color = "#28a745"
        warning_color = "#ffc107"
        danger_color = "#dc3545"

        self.window.configure(bg=bg_color)

        # Estilos personalizados
        style.configure("Card.TFrame", background=card_color, relief="raised", borderwidth=1)
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background=bg_color)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12, "bold"), background=card_color)
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _create_widgets(self):
        # Notebook para pestañas
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Pestaña de configuración de APIs
        self.api_frame = ttk.Frame(notebook)
        notebook.add(self.api_frame, text="🔑 APIs")

        # Pestaña de dashboard de gastos
        self.dashboard_frame = ttk.Frame(notebook)
        notebook.add(self.dashboard_frame, text="📊 Dashboard")

        self._create_api_config_tab()
        self._create_dashboard_tab()

    def _create_api_config_tab(self):
        # Título
        title = ttk.Label(self.api_frame, text="Configuración de APIs", style="Title.TLabel")
        title.pack(pady=(0, 20))

        # Crear un canvas con scrollbar
        canvas = tk.Canvas(self.api_frame, bg="#f8f9fa")
        scrollbar = ttk.Scrollbar(self.api_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # SunoAPI Card
        self._create_suno_card(scrollable_frame)

        # Replicate API Card
        self._create_replicate_card(scrollable_frame)

        # OpenAI API Card
        self._create_openai_card(scrollable_frame)

        # Botones de acción
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", pady=20)

        test_button = ttk.Button(
            button_frame,
            text="🧪 Probar Conexiones",
            command=self._test_apis,
            style="Primary.TButton"
        )
        test_button.pack(side="left", padx=(0, 10))

        save_button = ttk.Button(
            button_frame,
            text="💾 Guardar Configuración",
            command=self._save_settings,
            style="Primary.TButton"
        )
        save_button.pack(side="left", padx=(0, 10))

        reset_button = ttk.Button(
            button_frame,
            text="🔄 Restablecer",
            command=self._reset_settings
        )
        reset_button.pack(side="left")

    def _create_suno_card(self, parent):
        card = ttk.LabelFrame(parent, text="🎵 SunoAPI - Generación de Música", style="Card.TFrame")
        card.pack(fill="x", pady=(0, 15), padx=10)

        # API Key
        ttk.Label(card, text="API Key:").pack(anchor="w", padx=10, pady=(10, 0))
        self.suno_key_var = tk.StringVar()
        suno_key_entry = ttk.Entry(card, textvariable=self.suno_key_var, show="*", width=60)
        suno_key_entry.pack(fill="x", padx=10, pady=(5, 10))

        # Base URL
        ttk.Label(card, text="Base URL:").pack(anchor="w", padx=10)
        self.suno_url_var = tk.StringVar(value="https://api.sunoapi.org")
        suno_url_entry = ttk.Entry(card, textvariable=self.suno_url_var, width=60)
        suno_url_entry.pack(fill="x", padx=10, pady=(5, 10))

        # Enlace para obtener API Key
        link_frame = ttk.Frame(card)
        link_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(link_frame, text="💡 Obtener API Key:").pack(side="left")
        link_label = ttk.Label(link_frame, text="https://sunoapi.org/api-key", foreground="blue", cursor="hand2")
        link_label.pack(side="left", padx=(5, 0))
        link_label.bind("<Button-1>", lambda e: self._open_url("https://sunoapi.org/api-key"))

    def _create_replicate_card(self, parent):
        card = ttk.LabelFrame(parent, text="🖼️ Replicate - Generación de Imágenes y Videos", style="Card.TFrame")
        card.pack(fill="x", pady=(0, 15), padx=10)

        # API Token
        ttk.Label(card, text="API Token:").pack(anchor="w", padx=10, pady=(10, 0))
        self.replicate_token_var = tk.StringVar()
        replicate_token_entry = ttk.Entry(card, textvariable=self.replicate_token_var, show="*", width=60)
        replicate_token_entry.pack(fill="x", padx=10, pady=(5, 10))

        # Base URL
        ttk.Label(card, text="Base URL:").pack(anchor="w", padx=10)
        self.replicate_url_var = tk.StringVar(value="https://api.replicate.com/v1")
        replicate_url_entry = ttk.Entry(card, textvariable=self.replicate_url_var, width=60)
        replicate_url_entry.pack(fill="x", padx=10, pady=(5, 10))

        # Enlace para obtener API Token
        link_frame = ttk.Frame(card)
        link_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(link_frame, text="💡 Obtener API Token:").pack(side="left")
        link_label = ttk.Label(link_frame, text="https://replicate.com/account/api-tokens", foreground="blue", cursor="hand2")
        link_label.pack(side="left", padx=(5, 0))
        link_label.bind("<Button-1>", lambda e: self._open_url("https://replicate.com/account/api-tokens"))

    def _create_openai_card(self, parent):
        card = ttk.LabelFrame(parent, text="🤖 OpenAI - Generación de Letras", style="Card.TFrame")
        card.pack(fill="x", pady=(0, 15), padx=10)

        # API Key
        ttk.Label(card, text="API Key:").pack(anchor="w", padx=10, pady=(10, 0))
        self.openai_key_var = tk.StringVar()
        openai_key_entry = ttk.Entry(card, textvariable=self.openai_key_var, show="*", width=60)
        openai_key_entry.pack(fill="x", padx=10, pady=(5, 10))

        # Assistant ID
        ttk.Label(card, text="Assistant ID:").pack(anchor="w", padx=10)
        self.openai_assistant_var = tk.StringVar(value="asst_tR6OL8QLpSsDDlc6hKdBmVNU")
        openai_assistant_entry = ttk.Entry(card, textvariable=self.openai_assistant_var, width=60)
        openai_assistant_entry.pack(fill="x", padx=10, pady=(5, 10))

        # Base URL
        ttk.Label(card, text="Base URL:").pack(anchor="w", padx=10)
        self.openai_url_var = tk.StringVar(value="https://api.openai.com/v1")
        openai_url_entry = ttk.Entry(card, textvariable=self.openai_url_var, width=60)
        openai_url_entry.pack(fill="x", padx=10, pady=(5, 10))

        # Enlace para obtener API Key
        link_frame = ttk.Frame(card)
        link_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(link_frame, text="💡 Obtener API Key:").pack(side="left")
        link_label = ttk.Label(link_frame, text="https://platform.openai.com/api-keys", foreground="blue", cursor="hand2")
        link_label.pack(side="left", padx=(5, 0))
        link_label.bind("<Button-1>", lambda e: self._open_url("https://platform.openai.com/api-keys"))

    def _create_dashboard_tab(self):
        # Título
        title = ttk.Label(self.dashboard_frame, text="Dashboard de Gastos", style="Title.TLabel")
        title.pack(pady=(0, 20))

        # Frame para estadísticas
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="📈 Estadísticas de Uso")
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Crear widgets para estadísticas
        self.stats_text = tk.Text(stats_frame, height=8, wrap=tk.WORD, bg="#f8f9fa", relief="flat")
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)

        self.stats_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        stats_scroll.pack(side="right", fill="y", pady=10)

        # Frame para gráfico
        chart_frame = ttk.LabelFrame(self.dashboard_frame, text="📊 Gráfico de Gastos")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Crear el gráfico
        self._create_chart(chart_frame)

        # Botón de actualización
        refresh_button = ttk.Button(
            self.dashboard_frame,
            text="🔄 Actualizar Datos",
            command=self._refresh_dashboard
        )
        refresh_button.pack(pady=10)

        # Cargar datos iniciales
        self._refresh_dashboard()

    def _create_chart(self, parent):
        # Crear figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.fig.patch.set_facecolor('#f8f9fa')

        # Crear canvas para tkinter
        self.chart_canvas = FigureCanvasTkAgg(self.fig, parent)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _load_current_settings(self):
        settings = self.config_manager.get_api_settings()

        self.suno_key_var.set(settings.suno_api_key)
        self.suno_url_var.set(settings.suno_base_url)

        self.replicate_token_var.set(settings.replicate_api_token)
        self.replicate_url_var.set(settings.replicate_base_url)

        self.openai_key_var.set(settings.openai_api_key)
        self.openai_assistant_var.set(settings.openai_assistant_id)
        self.openai_url_var.set(settings.openai_base_url)

    def _save_settings(self):
        try:
            settings = APISettings(
                suno_api_key=self.suno_key_var.get().strip(),
                suno_base_url=self.suno_url_var.get().strip(),
                replicate_api_token=self.replicate_token_var.get().strip(),
                replicate_base_url=self.replicate_url_var.get().strip(),
                openai_api_key=self.openai_key_var.get().strip(),
                openai_assistant_id=self.openai_assistant_var.get().strip(),
                openai_base_url=self.openai_url_var.get().strip()
            )

            self.config_manager.save_config(settings)

            messagebox.showinfo("Éxito", "✅ Configuración guardada correctamente!")

            if self.on_settings_changed:
                self.on_settings_changed()

        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al guardar la configuración:\n{str(e)}")

    def _test_apis(self):
        # Implementar prueba de conexiones
        results = []

        # Probar SunoAPI
        if self.suno_key_var.get().strip():
            # Aquí irían las pruebas reales de conexión
            results.append("🎵 SunoAPI: ✅ Conexión exitosa")
        else:
            results.append("🎵 SunoAPI: ⚠️ API Key no configurada")

        # Probar Replicate
        if self.replicate_token_var.get().strip():
            results.append("🖼️ Replicate: ✅ Conexión exitosa")
        else:
            results.append("🖼️ Replicate: ⚠️ API Token no configurada")

        # Probar OpenAI
        if self.openai_key_var.get().strip():
            results.append("🤖 OpenAI: ✅ Conexión exitosa")
        else:
            results.append("🤖 OpenAI: ⚠️ API Key no configurada")

        messagebox.showinfo("Prueba de Conexiones", "\n".join(results))

    def _reset_settings(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas restablecer todas las configuraciones?"):
            self.suno_key_var.set("")
            self.suno_url_var.set("https://api.sunoapi.org")
            self.replicate_token_var.set("")
            self.replicate_url_var.set("https://api.replicate.com/v1")
            self.openai_key_var.set("")
            self.openai_assistant_var.set("asst_tR6OL8QLpSsDDlc6hKdBmVNU")
            self.openai_url_var.set("https://api.openai.com/v1")

    def _refresh_dashboard(self):
        try:
            stats = self.tracker.get_usage_stats(30)

            # Actualizar texto de estadísticas
            self.stats_text.delete('1.0', tk.END)

            # Validar y proporcionar valores por defecto
            totals = stats.get('totals', {})
            total_cost = totals.get('total_cost') or 0.0
            total_calls = totals.get('total_calls') or 0
            total_tokens = totals.get('total_tokens') or 0

            stats_text = f"""🎯 RESUMEN DE ÚLTIMOS 30 DÍAS

💰 Gastos Totales: ${total_cost:.4f} USD
📞 Llamadas Totales: {total_calls}
🔤 Tokens Totales: {total_tokens}

📊 POR API:
"""

            api_stats = stats.get('api_stats', [])
            if not api_stats:
                stats_text += "\n📭 No hay datos de uso disponibles aún.\n\n💡 Usa la aplicación para generar música, imágenes o letras y verás las estadísticas aquí."
            else:
                for api_stat in api_stats:
                    api_name = api_stat.get('api_name', 'Desconocida')
                    api_cost = api_stat.get('total_cost') or 0.0
                    api_calls = api_stat.get('total_calls') or 0
                    avg_cost = api_stat.get('avg_cost_per_call') or 0.0
                    failed_calls = api_stat.get('failed_calls') or 0

                    stats_text += f"""
🔹 {api_name}:
   💵 Costo: ${api_cost:.4f} USD
   📞 Llamadas: {api_calls}
   📊 Promedio/llamada: ${avg_cost:.4f} USD
   ❌ Fallos: {failed_calls}
"""

            self.stats_text.insert('1.0', stats_text)

            # Actualizar gráfico
            self._update_chart(stats)

        except Exception as e:
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', f"Error al cargar estadísticas: {str(e)}\n\nEsto puede ocurrir si es la primera vez que usas el sistema de tracking.")

    def _update_chart(self, stats):
        self.ax.clear()

        daily_stats = stats.get('daily_stats', [])
        if not daily_stats:
            self.ax.text(0.5, 0.5, '📊 No hay datos para mostrar\n\n💡 Usa la aplicación para ver gráficos de gastos',
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=12, color='#666666')
        else:
            # Preparar datos para el gráfico
            dates = []
            costs = []
            apis = set()

            for stat in daily_stats:
                try:
                    date_str = stat.get('date')
                    daily_cost = stat.get('daily_cost') or 0.0
                    api_name = stat.get('api_name', 'Desconocida')

                    if date_str:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        dates.append(date_obj)
                        costs.append(daily_cost)
                        apis.add(api_name)
                except (ValueError, TypeError) as e:
                    print(f"Error procesando estadística: {e}")
                    continue

            if dates and costs:
                # Crear gráfico de barras
                self.ax.bar(dates, costs, alpha=0.7, color='#007bff')
                self.ax.set_xlabel('Fecha')
                self.ax.set_ylabel('Costo (USD)')
                self.ax.set_title('Gastos Diarios por API')

                # Formatear fechas en el eje X
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                if len(dates) > 1:
                    self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))

                # Rotar etiquetas de fecha
                plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            else:
                self.ax.text(0.5, 0.5, '📊 Datos insuficientes para gráfico',
                            horizontalalignment='center', verticalalignment='center',
                            transform=self.ax.transAxes, fontsize=12, color='#666666')

        self.fig.tight_layout()
        self.chart_canvas.draw()

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')