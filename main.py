import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class FileCollectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сборщик текстовых и кодовых файлов, v0.1")
        self.root.geometry("700x500")

        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

        title_label = ttk.Label(main_frame, text="Сборщик текстовых и кодовых файлов",
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(main_frame, text="Целевая папка:").grid(row=1, column=0, sticky=tk.W, pady=5)

        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(main_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))

        self.browse_button = ttk.Button(main_frame, text="Обзор", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, pady=5)

        ttk.Label(main_frame, text="Расширения файлов (через запятую):").grid(row=2, column=0, sticky=tk.W, pady=5)

        self.extensions_var = tk.StringVar(
            value=".txt,.py,.js,.java,.cpp,.c,.h,.html,.css,.php,.xml,.json,.csv,.md,.sql,.rb,.go,.rs,.ts,.jsx,.tsx,.yml,.yaml,.ini,.cfg,.conf,.bat,.sh,.ps1,.log,.web,.bot")
        self.extensions_entry = ttk.Entry(main_frame, textvariable=self.extensions_var, width=50)
        self.extensions_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(main_frame, text="Игнорируемые папки (через запятую):").grid(row=3, column=0, sticky=tk.W, pady=5)

        self.ignore_folders_var = tk.StringVar(value=".git,.venv,__pycache__,node_modules,build,dist,.idea,.vscode")
        self.ignore_folders_entry = ttk.Entry(main_frame, textvariable=self.ignore_folders_var, width=50)
        self.ignore_folders_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        self.run_button = ttk.Button(button_frame, text="Собрать файлы", command=self.collect_files)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.merge_button = ttk.Button(button_frame, text="Объединить файлы", command=self.merge_files)
        self.merge_button.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

        ttk.Label(main_frame, text="Лог выполнения:").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))

        self.log_text = tk.Text(main_frame, height=12, width=80)
        self.log_text.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=8, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def browse_folder(self):
        """Открывает диалог выбора папки"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def log_message(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def should_ignore_folder(self, folder_name, ignore_list):
        """Проверяет, нужно ли игнорировать папку"""
        return folder_name in ignore_list

    def collect_files(self):
        """Основная функция сбора файлов"""
        folder_path = self.folder_path.get()

        if not folder_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите папку")
            return

        if not os.path.exists(folder_path):
            messagebox.showerror("Ошибка", "Указанная папка не существует")
            return

        extensions = [ext.strip().lower() for ext in self.extensions_var.get().split(",")]
        ignore_folders = [folder.strip() for folder in self.ignore_folders_var.get().split(",")]

        self.run_button.config(state='disabled')
        self.merge_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("Сбор файлов...")
        self.log_text.delete(1.0, tk.END)

        try:
            output_file = self.process_folder(folder_path, extensions, ignore_folders)
            messagebox.showinfo("Успех", f"Файлы успешно собраны в:\n{output_file}")
            self.status_var.set("Готово!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
            self.status_var.set("Ошибка")

        finally:
            self.progress.stop()
            self.run_button.config(state='normal')
            self.merge_button.config(state='normal')

    def merge_files(self):
        """Функция для объединения файлов с новым форматом"""
        folder_path = self.folder_path.get()

        if not folder_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите папку")
            return

        if not os.path.exists(folder_path):
            messagebox.showerror("Ошибка", "Указанная папка не существует")
            return

        extensions = [ext.strip().lower() for ext in self.extensions_var.get().split(",")]
        ignore_folders = [folder.strip() for folder in self.ignore_folders_var.get().split(",")]

        self.run_button.config(state='disabled')
        self.merge_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("Объединение файлов...")
        self.log_text.delete(1.0, tk.END)

        try:
            output_file = self.merge_files_with_new_format(folder_path, extensions, ignore_folders)
            messagebox.showinfo("Успех", f"Файлы успешно объединены в:\n{output_file}")
            self.status_var.set("Готово!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
            self.status_var.set("Ошибка")

        finally:
            self.progress.stop()
            self.run_button.config(state='normal')
            self.merge_button.config(state='normal')

    def process_folder(self, folder_path, extensions, ignore_folders):
        """Рекурсивно обрабатывает папку и собирает файлы"""
        output_file = os.path.join(folder_path, "collected_files.txt")

        self.log_message(f"Начинаем сбор файлов из: {folder_path}")
        self.log_message(f"Ищем файлы с расширениями: {', '.join(extensions)}")
        self.log_message(f"Игнорируем папки: {', '.join(ignore_folders)}")

        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("=" * 80 + "\n")
            outfile.write(f"СОБРАННЫЕ ФАЙЛЫ ИЗ ПАПКИ: {folder_path}\n")
            outfile.write("=" * 80 + "\n\n")

            file_count = 0
            total_size = 0

            for root_dir, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if not self.should_ignore_folder(d, ignore_folders)]

                for file in files:
                    file_path = os.path.join(root_dir, file)

                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in extensions:
                        try:

                            rel_path = os.path.relpath(file_path, folder_path)

                            self.log_message(f"Обрабатывается: {rel_path}")

                            outfile.write("\n" + "=" * 80 + "\n")
                            outfile.write(f"ФАЙЛ: {rel_path}\n")
                            outfile.write("=" * 80 + "\n\n")

                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                outfile.write(content)

                                if content and not content.endswith('\n'):
                                    outfile.write('\n')

                            file_count += 1
                            total_size += os.path.getsize(file_path)

                        except UnicodeDecodeError:
                            self.log_message(f"Ошибка кодировки: {file_path} (пропущен)")
                        except Exception as e:
                            self.log_message(f"Ошибка обработки {file_path}: {str(e)}")

            outfile.write("\n" + "=" * 80 + "\n")
            outfile.write("СТАТИСТИКА\n")
            outfile.write("=" * 80 + "\n")
            outfile.write(f"Всего обработано файлов: {file_count}\n")
            outfile.write(f"Общий размер: {total_size} байт ({total_size / 1024 / 1024:.2f} МБ)\n")
            outfile.write(f"Выходной файл: {output_file}\n")
            outfile.write("Сделано github/L1ghtsitte, ТГК: @hellsfrik")

        self.log_message(f"\nСбор завершен!")
        self.log_message(f"Обработано файлов: {file_count}")
        self.log_message(f"Общий размер: {total_size} байт")
        self.log_message(f"Результат сохранен в: {output_file}")
        self.log_message(f"Сделано github/L1ghtsitte, ТГК: @hellsfrik")

        return output_file

    def merge_files_with_new_format(self, folder_path, extensions, ignore_folders):
        """Объединяет файлы с новым форматом заголовков"""
        output_file = os.path.join(folder_path, "merged_files.txt")

        self.log_message(f"Начинаем объединение файлов из: {folder_path}")
        self.log_message(f"Ищем файлы с расширениями: {', '.join(extensions)}")
        self.log_message(f"Игнорируем папки: {', '.join(ignore_folders)}")

        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("=" * 80 + "\n")
            outfile.write(f"ОБЪЕДИНЕННЫЕ ФАЙЛЫ ИЗ ПАПКИ: {folder_path}\n")
            outfile.write("=" * 80 + "\n\n")

            file_count = 0
            total_size = 0

            for root_dir, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if not self.should_ignore_folder(d, ignore_folders)]

                for file in files:
                    file_path = os.path.join(root_dir, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in extensions:
                        try:

                            rel_path = os.path.relpath(file_path, folder_path)
                            self.log_message(f"Объединяется: {rel_path}")
                            outfile.write("\n" + "=" * 60 + "\n")
                            outfile.write(f"======={rel_path}=======\n")
                            outfile.write("=" * 60 + "\n\n")
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                outfile.write(content)

                                if content and not content.endswith('\n'):
                                    outfile.write('\n')

                            file_count += 1
                            total_size += os.path.getsize(file_path)

                        except UnicodeDecodeError:
                            self.log_message(f"Ошибка кодировки: {file_path} (пропущен)")
                        except Exception as e:
                            self.log_message(f"Ошибка обработки {file_path}: {str(e)}")

            outfile.write("\n" + "=" * 80 + "\n")
            outfile.write("СТАТИСТИКА\n")
            outfile.write("=" * 80 + "\n")
            outfile.write(f"Всего объединено файлов: {file_count}\n")
            outfile.write(f"Общий размер: {total_size} байт ({total_size / 1024 / 1024:.2f} МБ)\n")
            outfile.write(f"Выходной файл: {output_file}\n")
            outfile.write("Сделано github/L1ghtsitte, ТГК: @hellsfrik")

        self.log_message(f"\nОбъединение завершено!")
        self.log_message(f"Объединено файлов: {file_count}")
        self.log_message(f"Общий размер: {total_size} байт")
        self.log_message(f"Результат сохранен в: {output_file}")
        self.log_message(f"Сделано github/L1ghtsitte, ТГК: @hellsfrik")

        return output_file


def main():
    root = tk.Tk()
    app = FileCollectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()