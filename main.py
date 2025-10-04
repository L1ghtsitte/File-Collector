import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import datetime
import threading
from collections import defaultdict


class FileCollectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сборщик текстовых и кодовых файлов v2.0")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Стиль
        self.setup_styles()
        
        # Переменные
        self.is_processing = False
        self.current_thread = None
        
        self.setup_ui()

    def setup_styles(self):
        """Настройка стилей для интерфейса"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Arial", 10, "italic"), foreground="gray")
        style.configure("Stats.TLabel", font=("Consolas", 9))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")

    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Конфигурация весов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="📁 Сборщик текстовых и кодовых файлов", 
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        subtitle_label = ttk.Label(main_frame, 
                                  text="Собирает и анализирует файлы с сохранением форматирования",
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        # Панель настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки сбора", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="Целевая папка:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(settings_frame, textvariable=self.folder_path)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        self.browse_button = ttk.Button(settings_frame, text="Обзор", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, pady=5)

        ttk.Label(settings_frame, text="Расширения файлов:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.extensions_var = tk.StringVar(
            value=".txt,.py,.js,.java,.cpp,.c,.h,.html,.css,.php,.xml,.json,.csv,.md,.sql,.rb,.go,.rs,.ts,.jsx,.tsx,.yml,.yaml,.ini,.cfg,.conf,.bat,.sh,.ps1,.log")
        self.extensions_entry = ttk.Entry(settings_frame, textvariable=self.extensions_var)
        self.extensions_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(settings_frame, text="Игнорируемые папки:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ignore_folders_var = tk.StringVar(value=".git,.venv,__pycache__,node_modules,build,dist,.idea,.vscode,target,out,bin,obj")
        self.ignore_folders_entry = ttk.Entry(settings_frame, textvariable=self.ignore_folders_var)
        self.ignore_folders_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=3, pady=15)

        self.collect_button = ttk.Button(action_frame, text="📂 Собрать файлы", 
                                        command=self.start_collect_files, width=15)
        self.collect_button.pack(side=tk.LEFT, padx=5)

        self.merge_button = ttk.Button(action_frame, text="🔄 Объединить файлы", 
                                      command=self.start_merge_files, width=15)
        self.merge_button.pack(side=tk.LEFT, padx=5)

        self.settings_button = ttk.Button(action_frame, text="⚙️ Настройки вывода", 
                                         command=self.show_settings, width=15)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)

        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding="5")
        stats_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 5))
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(stats_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
 
        log_frame = ttk.Frame(notebook, padding="5")
        notebook.add(log_frame, text="Лог выполнения")
        
        self.log_text = tk.Text(log_frame, height=12, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
 
        stats_display_frame = ttk.Frame(notebook, padding="5")
        notebook.add(stats_display_frame, text="Детальная статистика")
        
        self.stats_text = tk.Text(stats_display_frame, height=12, wrap=tk.WORD, font=("Consolas", 9))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        stats_scrollbar = ttk.Scrollbar(stats_display_frame, orient="vertical", command=self.stats_text.yview)
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        stats_display_frame.columnconfigure(0, weight=1)
        stats_display_frame.rowconfigure(0, weight=1)

        log_buttons_frame = ttk.Frame(stats_frame)
        log_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))

        ttk.Button(log_buttons_frame, text="Очистить лог", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons_frame, text="Экспорт лога", command=self.export_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons_frame, text="Копировать статистику", command=self.copy_stats).pack(side=tk.LEFT, padx=2)

        self.stats_var = tk.StringVar(value="Файлов: 0 | Строк: 0 | Слов: 0 | Символов: 0")
        self.stats_label = ttk.Label(main_frame, textvariable=self.stats_var, style="Stats.TLabel")
        self.stats_label.grid(row=7, column=0, columnspan=3, pady=(5, 0))

    def browse_folder(self):
        """Открывает диалог выбора папки"""
        folder_selected = filedialog.askdirectory(title="Выберите целевую папку")
        if folder_selected:
            self.folder_path.set(folder_selected)

    def log_message(self, message, message_type="info"):
        """Добавляет сообщение в лог с временной меткой"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if message_type == "error":
            prefix = f"[{timestamp}] ❌ "
        elif message_type == "warning":
            prefix = f"[{timestamp}] ⚠️ "
        elif message_type == "success":
            prefix = f"[{timestamp}] ✅ "
        else:
            prefix = f"[{timestamp}] ℹ️ "
        
        self.log_text.insert(tk.END, prefix + message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def clear_log(self):
        """Очищает лог"""
        self.log_text.delete(1.0, tk.END)

    def export_log(self):
        """Экспортирует лог в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Экспорт лога"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Лог экспортирован в: {filename}", "success")
            except Exception as e:
                self.log_message(f"Ошибка экспорта: {str(e)}", "error")

    def copy_stats(self):
        """Копирует статистику в буфер обмена"""
        stats = self.stats_text.get(1.0, tk.END)
        if stats.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(stats)
            self.log_message("Статистика скопирована в буфер обмена", "success")

    def show_settings(self):
        """Показывает диалог настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки вывода")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()

        ttk.Label(settings_window, text="Настройки формата вывода").pack(pady=10)

        
        ttk.Label(settings_window, text="Дополнительные настройки будут добавлены в будущих версиях", 
                 foreground="gray").pack(pady=20)

        ttk.Button(settings_window, text="Закрыть", 
                  command=settings_window.destroy).pack(pady=10)

    def should_ignore_folder(self, folder_name, ignore_list):
        """Проверяет, нужно ли игнорировать папку"""
        return folder_name in ignore_list

    def get_file_stats(self, file_path):
        """Собирает полную статистику по файлу с сохранением табуляции"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Статистика
            lines = content.split('\n')
            line_count = len(lines)
            word_count = len(content.split())
            char_count = len(content)
            char_no_whitespace_count = len(content.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', ''))
            
            
            tab_count = content.count('\t')
            
            return {
                'lines': line_count,
                'words': word_count,
                'chars_total': char_count,
                'chars_no_whitespace': char_no_whitespace_count,
                'tabs': tab_count,
                'size': os.path.getsize(file_path),
                'content': content
            }
        except Exception as e:
            self.log_message(f"Ошибка чтения {file_path}: {str(e)}", "error")
            return None

    def start_collect_files(self):
        """Запускает сбор файлов в отдельном потоке"""
        if self.is_processing:
            return
            
        if not self.validate_input():
            return
            
        self.is_processing = True
        self.update_ui_state()
        
        self.current_thread = threading.Thread(target=self.collect_files)
        self.current_thread.daemon = True
        self.current_thread.start()

    def start_merge_files(self):
        """Запускает объединение файлов в отдельном потоке"""
        if self.is_processing:
            return
            
        if not self.validate_input():
            return
            
        self.is_processing = True
        self.update_ui_state()
        
        self.current_thread = threading.Thread(target=self.merge_files)
        self.current_thread.daemon = True
        self.current_thread.start()

    def validate_input(self):
        """Проверяет корректность ввода"""
        folder_path = self.folder_path.get()

        if not folder_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите папку")
            return False

        if not os.path.exists(folder_path):
            messagebox.showerror("Ошибка", "Указанная папка не существует")
            return False

        return True

    def update_ui_state(self):
        """Обновляет состояние UI в зависимости от процесса"""
        if self.is_processing:
            self.collect_button.config(state='disabled')
            self.merge_button.config(state='disabled')
            self.settings_button.config(state='disabled')
            self.browse_button.config(state='disabled')
            self.progress.start()
        else:
            self.collect_button.config(state='normal')
            self.merge_button.config(state='normal')
            self.settings_button.config(state='normal')
            self.browse_button.config(state='normal')
            self.progress.stop()

    def collect_files(self):
        """Основная функция сбора файлов"""
        try:
            folder_path = self.folder_path.get()
            extensions = [ext.strip().lower() for ext in self.extensions_var.get().split(",")]
            ignore_folders = [folder.strip() for folder in self.ignore_folders_var.get().split(",")]

            self.status_var.set("Сбор файлов...")
            self.log_text.delete(1.0, tk.END)
            self.stats_text.delete(1.0, tk.END)
            
            self.log_message(f"Начинаем сбор файлов из: {folder_path}")
            self.log_message(f"Ищем файлы с расширениями: {', '.join(extensions)}")
            self.log_message(f"Игнорируем папки: {', '.join(ignore_folders)}")

            output_file = os.path.join(folder_path, "collected_files.txt")
            result = self.process_folder(folder_path, extensions, ignore_folders, output_file)
            
            if result:
                messagebox.showinfo("Успех", f"Файлы успешно собраны в:\n{output_file}")
                self.status_var.set("Готово!")
                self.log_message("Сбор файлов завершен успешно!", "success")
            else:
                messagebox.showwarning("Предупреждение", "Не удалось собрать файлы или файлы не найдены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
            self.status_var.set("Ошибка")
            self.log_message(f"Критическая ошибка: {str(e)}", "error")
        finally:
            self.is_processing = False
            self.root.after(0, self.update_ui_state)

    def merge_files(self):
        """Функция для объединения файлов с новым форматом"""
        try:
            folder_path = self.folder_path.get()
            extensions = [ext.strip().lower() for ext in self.extensions_var.get().split(",")]
            ignore_folders = [folder.strip() for folder in self.ignore_folders_var.get().split(",")]

            self.status_var.set("Объединение файлов...")
            self.log_text.delete(1.0, tk.END)
            self.stats_text.delete(1.0, tk.END)
            
            self.log_message(f"Начинаем объединение файлов из: {folder_path}")
            self.log_message(f"Ищем файлы с расширениями: {', '.join(extensions)}")
            self.log_message(f"Игнорируем папки: {', '.join(ignore_folders)}")

            output_file = os.path.join(folder_path, "merged_files.txt")
            result = self.merge_files_with_new_format(folder_path, extensions, ignore_folders, output_file)
            
            if result:
                messagebox.showinfo("Успех", f"Файлы успешно объединены в:\n{output_file}")
                self.status_var.set("Готово!")
                self.log_message("Объединение файлов завершено успешно!", "success")
            else:
                messagebox.showwarning("Предупреждение", "Не удалось объединить файлы или файлы не найдены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
            self.status_var.set("Ошибка")
            self.log_message(f"Критическая ошибка: {str(e)}", "error")
        finally:
            self.is_processing = False
            self.root.after(0, self.update_ui_state)

    def process_folder(self, folder_path, extensions, ignore_folders, output_file):
        """Рекурсивно обрабатывает папку и собирает файлы с сохранением табуляции"""
        total_stats = {
            'files': 0, 'lines': 0, 'words': 0, 'chars_total': 0, 
            'chars_no_whitespace': 0, 'size': 0, 'tabs': 0
        }
        
        file_stats = []

        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Заголовок
            outfile.write("=" * 80 + "\n")
            outfile.write(f"СОБРАННЫЕ ФАЙЛЫ ИЗ ПАПКИ: {folder_path}\n")
            outfile.write(f"ВРЕМЯ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            outfile.write("=" * 80 + "\n\n")

            
            for root_dir, dirs, files in os.walk(folder_path):
                
                dirs[:] = [d for d in dirs if not self.should_ignore_folder(d, ignore_folders)]

                for file in files:
                    if self.is_processing == False:  
                        return False
                        
                    file_path = os.path.join(root_dir, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in extensions:
                        try:
                            rel_path = os.path.relpath(file_path, folder_path)
                            self.log_message(f"Обрабатывается: {rel_path}")

                         
                            stats = self.get_file_stats(file_path)
                            if stats is None:
                                continue

                            
                            outfile.write("\n" + "=" * 80 + "\n")
                            outfile.write(f"ФАЙЛ: {rel_path}\n")
                            outfile.write("=" * 80 + "\n\n")
                            outfile.write(stats['content'])
                            
                            if stats['content'] and not stats['content'].endswith('\n'):
                                outfile.write('\n')

                             total_stats['files'] += 1
                            total_stats['lines'] += stats['lines']
                            total_stats['words'] += stats['words']
                            total_stats['chars_total'] += stats['chars_total']
                            total_stats['chars_no_whitespace'] += stats['chars_no_whitespace']
                            total_stats['size'] += stats['size']
                            total_stats['tabs'] += stats['tabs']
                            
                            file_stats.append({
                                'path': rel_path,
                                'stats': stats
                            })

                             self.update_progress_stats(total_stats)

                        except Exception as e:
                            self.log_message(f"Ошибка обработки {file_path}: {str(e)}", "error")

            outfile.write("\n" + "=" * 80 + "\n")
            outfile.write("ПОЛНАЯ СТАТИСТИКА\n")
            outfile.write("=" * 80 + "\n")
            self.write_detailed_stats(outfile, total_stats, file_stats)

        self.show_detailed_stats(total_stats, file_stats)
        
        self.log_message(f"\nСбор завершен! Обработано файлов: {total_stats['files']}")
        return total_stats['files'] > 0

    def merge_files_with_new_format(self, folder_path, extensions, ignore_folders, output_file):
        """Объединяет файлы с новым форматом заголовков"""
        total_stats = {
            'files': 0, 'lines': 0, 'words': 0, 'chars_total': 0, 
            'chars_no_whitespace': 0, 'size': 0, 'tabs': 0
        }
        
        file_stats = []

        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("=" * 80 + "\n")
            outfile.write(f"ОБЪЕДИНЕННЫЕ ФАЙЛЫ ИЗ ПАПКИ: {folder_path}\n")
            outfile.write(f"ВРЕМЯ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            outfile.write("=" * 80 + "\n\n")

            for root_dir, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if not self.should_ignore_folder(d, ignore_folders)]

                for file in files:
                    if self.is_processing == False:
                        return False
                        
                    file_path = os.path.join(root_dir, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in extensions:
                        try:
                            rel_path = os.path.relpath(file_path, folder_path)
                            self.log_message(f"Объединяется: {rel_path}")

                            stats = self.get_file_stats(file_path)
                            if stats is None:
                                continue

                            outfile.write("\n" + "=" * 60 + "\n")
                            outfile.write(f"======={rel_path}=======\n")
                            outfile.write("=" * 60 + "\n\n")
                            outfile.write(stats['content'])
                            
                            if stats['content'] and not stats['content'].endswith('\n'):
                                outfile.write('\n')

                            
                            total_stats['files'] += 1
                            total_stats['lines'] += stats['lines']
                            total_stats['words'] += stats['words']
                            total_stats['chars_total'] += stats['chars_total']
                            total_stats['chars_no_whitespace'] += stats['chars_no_whitespace']
                            total_stats['size'] += stats['size']
                            total_stats['tabs'] += stats['tabs']
                            
                            file_stats.append({
                                'path': rel_path,
                                'stats': stats
                            })

                            self.update_progress_stats(total_stats)

                        except Exception as e:
                            self.log_message(f"Ошибка обработки {file_path}: {str(e)}", "error")

            outfile.write("\n" + "=" * 80 + "\n")
            outfile.write("ПОЛНАЯ СТАТИСТИКА\n")
            outfile.write("=" * 80 + "\n")
            self.write_detailed_stats(outfile, total_stats, file_stats)

        self.show_detailed_stats(total_stats, file_stats)
        
        self.log_message(f"\nОбъединение завершено! Обработано файлов: {total_stats['files']}")
        return total_stats['files'] > 0

    def update_progress_stats(self, stats):
        """Обновляет статистику в реальном времени"""
        stats_text = f"Файлов: {stats['files']} | Строк: {stats['lines']} | Слов: {stats['words']} | Символов: {stats['chars_total']}"
        self.stats_var.set(stats_text)
        self.root.update()

    def write_detailed_stats(self, outfile, total_stats, file_stats):
        """Записывает детальную статистику в файл"""
        outfile.write(f"Всего обработано файлов: {total_stats['files']}\n")
        outfile.write(f"Общее количество строк: {total_stats['lines']:,}\n")
        outfile.write(f"Общее количество слов: {total_stats['words']:,}\n")
        outfile.write(f"Общее количество символов (с пробелами): {total_stats['chars_total']:,}\n")
        outfile.write(f"Общее количество символов (без пробелов): {total_stats['chars_no_whitespace']:,}\n")
        outfile.write(f"Количество табуляций: {total_stats['tabs']:,}\n")
        outfile.write(f"Общий размер: {total_stats['size']:,} байт ({total_stats['size'] / 1024 / 1024:.2f} МБ)\n")
        outfile.write(f"Средняя длина строки: {total_stats['lines'] and total_stats['chars_total']/total_stats['lines']:.1f} символов\n")
        outfile.write(f"Средняя длина слова: {total_stats['words'] and total_stats['chars_no_whitespace']/total_stats['words']:.1f} символов\n")
        outfile.write(f"Выходной файл: {os.path.basename(outfile.name)}\n")
        outfile.write(f"Сделано github/L1ghtsitte, ТГК: @hellsfrik\n\n")

        if file_stats:
            outfile.write("СТАТИСТИКА ПО ТИПАМ ФАЙЛОВ:\n")
            outfile.write("-" * 40 + "\n")
            
            ext_stats = defaultdict(lambda: {'count': 0, 'lines': 0, 'size': 0})
            for file_info in file_stats:
                ext = os.path.splitext(file_info['path'])[1].lower() or 'без расширения'
                ext_stats[ext]['count'] += 1
                ext_stats[ext]['lines'] += file_info['stats']['lines']
                ext_stats[ext]['size'] += file_info['stats']['size']
            
            for ext, stats in sorted(ext_stats.items()):
                outfile.write(f"{ext:8} | Файлов: {stats['count']:3} | Строк: {stats['lines']:6} | Размер: {stats['size']/1024:7.1f} КБ\n")

    def show_detailed_stats(self, total_stats, file_stats):
        """Показывает детальную статистику в UI"""
        stats_text = f"""ПОЛНАЯ СТАТИСТИКА ОБРАБОТКИ
{'-' * 50}

ОСНОВНЫЕ МЕТРИКИ:
• Файлов обработано: {total_stats['files']}
• Всего строк: {total_stats['lines']:,}
• Всего слов: {total_stats['words']:,}
• Символов (всего): {total_stats['chars_total']:,}
• Символов (без пробелов): {total_stats['chars_no_whitespace']:,}
• Табуляций: {total_stats['tabs']:,}
• Общий размер: {total_stats['size']:,} байт ({total_stats['size'] / 1024 / 1024:.2f} МБ)

СРЕДНИЕ ПОКАЗАТЕЛИ:
• Средняя длина строки: {total_stats['lines'] and total_stats['chars_total']/total_stats['lines']:.1f} символов
• Средняя длина слова: {total_stats['words'] and total_stats['chars_no_whitespace']/total_stats['words']:.1f} символов
• Средний размер файла: {total_stats['files'] and total_stats['size']/total_stats['files']:.0f} байт

СТАТИСТИКА ПО РАСШИРЕНИЯМ:
"""
        
        # Статистика по расширениям
        ext_stats = defaultdict(lambda: {'count': 0, 'lines': 0, 'size': 0})
        for file_info in file_stats:
            ext = os.path.splitext(file_info['path'])[1].lower() or 'без расширения'
            ext_stats[ext]['count'] += 1
            ext_stats[ext]['lines'] += file_info['stats']['lines']
            ext_stats[ext]['size'] += file_info['stats']['size']
        
        for ext, stats in sorted(ext_stats.items()):
            stats_text += f"• {ext:10} - {stats['count']:2} файлов, {stats['lines']:5} строк, {stats['size']/1024:7.1f} КБ\n"

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)


def main():
    root = tk.Tk()
    app = FileCollectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()