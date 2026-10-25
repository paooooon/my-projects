import base64
import subprocess
import threading
import tkinter as tk
import winsound
from tkinter import messagebox, simpledialog

ANNOUNCEMENT_VOICE_NAME = ''
ANNOUNCEMENT_RATE = 0


class SeatCounterApp:
    def __init__(self, root):
        self.root = root
        self.capacity = 0
        self.occupied = 0
        self.party_sizes = []
        self.waiting_queue = []
        self.next_wait_number = 1
        self.call_password = ''
        self.root.title('こちらの画面で、ぱおーんレストランの席案内を行っています。')
        self.root.geometry('800x820')
        self.root.minsize(680, 760)
        self.root.configure(bg='#f4f1e8')
        self._build_setup()

    def _build_setup(self):
        panel = tk.Frame(self.root, bg='#f4f1e8', padx=36, pady=48)
        panel.pack(fill='both', expand=True)
        tk.Label(
            panel,
            text='こちらの画面で、ぱおーんレストランの席案内を行っています。',
            font=('Yu Gothic UI', 25, 'bold'),
            bg='#f4f1e8',
            fg='#20352e',
        ).pack(anchor='w', pady=(0, 8))
        tk.Label(
            panel,
            text='呼び出し用パスワードを設定してください',
            font=('Yu Gothic UI', 13),
            bg='#f4f1e8',
            fg='#52645b',
        ).pack(anchor='w', pady=(0, 18))

        self.password_var = tk.StringVar()
        self.password_confirm_var = tk.StringVar()
        tk.Label(panel, text='パスワード', font=('Yu Gothic UI', 11),
                 bg='#f4f1e8', fg='#20352e').pack(anchor='w')
        tk.Entry(
            panel, textvariable=self.password_var, show='*',
            font=('Yu Gothic UI', 16), width=18, relief='solid', bd=1
        ).pack(anchor='w', pady=(4, 12))
        tk.Label(panel, text='確認のため、もう一度入力', font=('Yu Gothic UI', 11),
                 bg='#f4f1e8', fg='#20352e').pack(anchor='w')
        tk.Entry(
            panel, textvariable=self.password_confirm_var, show='*',
            font=('Yu Gothic UI', 16), width=18, relief='solid', bd=1
        ).pack(anchor='w', pady=(4, 14))
        self.setup_message = tk.Label(
            panel, text='', font=('Yu Gothic UI', 11), bg='#f4f1e8', fg='#b44536'
        )
        self.setup_message.pack(anchor='w', pady=(0, 8))
        tk.Button(
            panel, text='パスワードを設定', command=self._set_password,
            font=('Yu Gothic UI', 12, 'bold'), bg='#28745b', fg='white',
            activebackground='#1f604a', activeforeground='white',
            relief='flat', padx=20, pady=10
        ).pack(anchor='w')

    def _set_password(self):
        password = self.password_var.get()
        if not password:
            self.setup_message.config(text='パスワードを入力してください。')
            return
        if password != self.password_confirm_var.get():
            self.setup_message.config(text='2回のパスワードが一致しません。')
            return

        self.call_password = password
        for child in self.root.winfo_children():
            child.destroy()
        self._build_capacity_setup()

    def _build_capacity_setup(self):
        panel = tk.Frame(self.root, bg='#f4f1e8', padx=36, pady=48)
        panel.pack(fill='both', expand=True)
        tk.Label(
            panel, text='席数を設定してください',
            font=('Yu Gothic UI', 16, 'bold'), bg='#f4f1e8', fg='#20352e'
        ).pack(anchor='w', pady=(0, 18))
        self.capacity_var = tk.StringVar(value='20')
        tk.Entry(
            panel,
            textvariable=self.capacity_var,
            font=('Yu Gothic UI', 18),
            width=10,
            relief='solid',
            bd=1,
        ).pack(anchor='w', pady=(0, 14))
        tk.Button(
            panel,
            text='席数を設定',
            command=self._start,
            font=('Yu Gothic UI', 12, 'bold'),
            bg='#28745b',
            fg='white',
            activebackground='#1f604a',
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=10,
        ).pack(anchor='w')
        self.setup_message = tk.Label(
            panel, text='', font=('Yu Gothic UI', 11), bg='#f4f1e8', fg='#b44536'
        )
        self.setup_message.pack(anchor='w', pady=(12, 0))

    def _start(self):
        try:
            capacity = int(self.capacity_var.get())
        except ValueError:
            self.setup_message.config(text='席数を数字で入力してください。')
            return
        if capacity <= 0:
            self.setup_message.config(text='1以上の席数を入力してください。')
            return

        self.capacity = capacity
        for child in self.root.winfo_children():
            child.destroy()
        self._build_dashboard()

    def _build_dashboard(self):
        page = tk.Frame(self.root, bg='#f4f1e8', padx=28, pady=22)
        page.pack(fill='both', expand=True)
        header = tk.Frame(page, bg='#f4f1e8')
        header.pack(fill='x')
        tk.Label(
            header,
            text='こちらの画面で、ぱおーんレストランの席案内を行っています。',
            font=('Yu Gothic UI', 22, 'bold'),
            bg='#f4f1e8',
            fg='#20352e',
        ).pack(side='left', anchor='n', pady=(8, 0))
        self.waiting_notice_label = tk.Label(
            header, text='', font=('Yu Gothic UI', 16, 'bold'),
            bg='#f4f1e8', fg='#b44536'
        )
        self.waiting_notice_label.pack(side='left', padx=(24, 0), pady=(10, 0))

        summary = tk.Frame(page, bg='#f4f1e8', pady=16)
        summary.pack(fill='x')
        self.remaining_label = tk.Label(
            summary, text='', font=('Yu Gothic UI', 20, 'bold'),
            bg='#f4f1e8', fg='#28745b'
        )
        self.remaining_label.pack(side='left')
        self.waiting_label = tk.Label(
            summary, text='', font=('Yu Gothic UI', 15, 'bold'),
            bg='#f4f1e8', fg='#52645b'
        )
        self.waiting_label.pack(side='left', padx=(20, 0))
        self.status_label = tk.Label(
            summary, text='', font=('Yu Gothic UI', 14, 'bold'),
            bg='#f4f1e8', fg="#b64637"
        )
        self.status_label.pack(side='right')

        called_panel = tk.Frame(page, bg='#dce9df', padx=16, pady=10)
        called_panel.pack(fill='x', pady=(0, 10))
        tk.Label(
            called_panel, text='呼び出し番号', font=('Yu Gothic UI', 13, 'bold'),
            bg='#dce9df', fg='#20352e'
        ).pack(anchor='w')
        self.called_number_label = tk.Label(
            called_panel, text='なし', font=('Yu Gothic UI', 22, 'bold'),
            bg='#dce9df', fg='#28745b', wraplength=680, justify='left'
        )
        self.called_number_label.pack(anchor='w')

        self.selected_action = None
        self.content = tk.Frame(page, bg='#f4f1e8')
        self.content.pack(fill='x', expand=False)

        self.action_frame = tk.Frame(self.content, bg='#f4f1e8', pady=10)
        tk.Label(
            self.action_frame, text='操作を選んでください',
            font=('Yu Gothic UI', 18, 'bold'), bg='#f4f1e8', fg='#20352e'
        ).pack(anchor='w', pady=(0, 8))
        actions = tk.Frame(self.action_frame, bg='#f4f1e8')
        actions.pack(fill='x')
        for action in ('enter', 'leave', 'call'):
            canvas = self._make_action_canvas(actions, action)
            canvas.pack(side='left', fill='both', expand=True, padx=4)

        self.input_frame = tk.Frame(self.content, bg='#f4f1e8', pady=10)
        count_row = tk.Frame(self.input_frame, bg='#f4f1e8', pady=8)
        count_row.pack(fill='x')
        tk.Label(
            count_row, text='人数', font=('Yu Gothic UI', 13, 'bold'),
            bg='#f4f1e8', fg='#20352e'
        ).pack(side='left', padx=(0, 12))
        self.count_var = tk.StringVar(value='')
        self.count_input = tk.Entry(
            count_row, textvariable=self.count_var, width=8,
            font=('Yu Gothic UI', 18, 'bold'), justify='center',
            state='readonly', readonlybackground='white', relief='solid', bd=1
        )
        self.count_input.pack(side='left')

        controls = tk.Frame(self.input_frame, bg='#f4f1e8', pady=8)
        controls.pack(fill='x')
        keypad = tk.Frame(controls, bg='#f4f1e8')
        keypad.pack(side='left', padx=(0, 24))
        keys = (
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('C', 3, 0), ('0', 3, 1), ('←', 3, 2),
        )
        for label, row, column in keys:
            if label == 'C':
                command = self._clear_count
            elif label == '←':
                command = self._backspace_count
            else:
                command = lambda digit=label: self._press_digit(digit)
            tk.Button(
                keypad, text=label, command=command, width=4, height=1,
                font=('Yu Gothic UI', 14, 'bold'), bg='white', fg='#20352e',
                activebackground='#dce9df', relief='solid', bd=1, cursor='hand2'
            ).grid(row=row, column=column, padx=3, pady=3, sticky='nsew')

        self.confirm_button = tk.Button(
            controls, text='確定', command=self._confirm_action,
            font=('Yu Gothic UI', 15, 'bold'),
            bg='#28745b', fg='white', activebackground='#1f604a',
            activeforeground='white', relief='flat', padx=28, pady=14,
            cursor='hand2'
        )
        self.confirm_button.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.back_button = tk.Button(
            controls, text='戻る', command=self._back_to_actions,
            font=('Yu Gothic UI', 14, 'bold'), bg='white', fg='#20352e',
            activebackground='#dce9df', relief='solid', bd=1,
            padx=24, pady=14, cursor='hand2'
        )
        self.back_button.pack(side='left', fill='x', expand=True, padx=(8, 0))

        tk.Label(
            page, text='案内', font=('Yu Gothic UI', 16, 'bold'),
            bg='#f4f1e8', fg='#20352e'
        ).pack(anchor='w', pady=(8, 5))
        self.log = tk.Text(
            page, height=8, wrap='word', font=('Yu Gothic UI', 16),
            bg='white', fg='#20352e', relief='solid', bd=1, state='disabled'
        )
        self.log.pack(fill='both', expand=True)
        self.action_frame.pack(fill='x')
        self._refresh('受付または退店登録を選び、人数を入力してください。')

    def _make_action_canvas(self, parent, action):
        canvas = tk.Canvas(
            parent, width=210, height=210, bg='white', highlightthickness=1,
            highlightbackground='#d3d8cf', cursor='hand2'
        )
        center = 105
        canvas.create_oval(center - 20, 22, center + 20, 62, fill='#d49a56', outline='')
        canvas.create_line(center, 64, center, 125, fill='#28745b', width=14, capstyle='round')
        canvas.create_line(center, 78, center - 34, 105, fill='#28745b', width=9, capstyle='round')
        canvas.create_line(center, 78, center + 34, 105, fill='#28745b', width=9, capstyle='round')
        canvas.create_line(center, 123, center - 25, 158, fill='#20352e', width=9, capstyle='round')
        canvas.create_line(center, 123, center + 25, 158, fill='#20352e', width=9, capstyle='round')

        if action == 'enter':
            canvas.create_line(24, 99, 61, 99, fill='#d36a45', width=5, arrow=tk.LAST)
            label = '受付'
        elif action == 'leave':
            canvas.create_line(149, 99, 186, 99, fill='#d36a45', width=5, arrow=tk.LAST)
            label = '退店登録'
        else:
            canvas.create_line(24, 99, 61, 99, fill='#d36a45', width=5, arrow=tk.LAST)
            label = '空席案内の呼び出し'

        canvas.create_text(
            center, 184, text=label, font=('Yu Gothic UI', 16, 'bold'),
            fill='#20352e'
        )
        canvas.bind('<Button-1>', lambda _event: self._select_action(action))
        canvas.bind('<Enter>', lambda _event: canvas.config(bg='#edf4ee'))
        canvas.bind('<Leave>', lambda _event: canvas.config(bg='white'))
        return canvas

    def _select_action(self, action):
        if action == 'call':
            self._authorize_call()
            return
        self.selected_action = action
        label = '受付' if action == 'enter' else '退店登録'
        self.count_var.set('')
        self.action_frame.pack_forget()
        self.input_frame.pack(fill='x')
        self._refresh(f'{label}の人数を数字ボタンで入力してください。')

    def _authorize_call(self):
        password = simpledialog.askstring(
            'パスワード確認', '呼び出し用パスワードを入力してください。',
            show='*', parent=self.root
        )
        if password is None:
            return
        if password != self.call_password:
            messagebox.showerror(
                'パスワードエラー', 'パスワードが違います。', parent=self.root
            )
            return
        self._call_waiting()

    def _confirm_action(self):
        if self.selected_action == 'enter':
            self._enter()
        elif self.selected_action == 'leave':
            self._leave()
        else:
            self._refresh('先に受付または退店登録を選んでください。')

    def _reset_selection(self):
        self.count_var.set('')
        self.selected_action = None
        self.input_frame.pack_forget()
        self.action_frame.pack(fill='x')

    def _back_to_actions(self):
        self._reset_selection()
        self._refresh('受付、退店登録、空席案内の呼び出しから選んでください。')

    def _update_waiting_notice(self):
        if self.waiting_queue:
            wait_number = self.waiting_queue[-1][0]
            notice = f'受付番号{wait_number}番でお待ちください。'
        else:
            notice = ''
        self.waiting_notice_label.config(text=notice)

    def _press_digit(self, digit):
        current = self.count_var.get()
        if current == '0':
            self.count_var.set(digit)
        else:
            self.count_var.set(current + digit)

    def _clear_count(self):
        self.count_var.set('')

    def _backspace_count(self):
        current = self.count_var.get()
        self.count_var.set(current[:-1])

    def _selected_count(self):
        value = self.count_var.get()
        if not value:
            self._refresh('人数を入力してください。')
            return None
        try:
            count = int(value)
        except ValueError:
            self._refresh('人数は数字で入力してください。')
            return None
        if count <= 0:
            self._refresh('1人以上を選んでください。')
            return None
        return count

    def _enter(self):
        count = self._selected_count()
        if count is None:
            return
        if self.waiting_queue:
            answer = messagebox.askyesno(
                '順番待ちの確認',
                f'{len(self.waiting_queue)}組待っています。'
                '順番待ちになりますが、受付しますか？'
            )
            if not answer:
                self._reset_selection()
                self._refresh('受付をキャンセルしました。')
                return

        remaining = self.capacity - self.occupied
        if self.waiting_queue or count > remaining:
            wait_number = self.next_wait_number
            self.next_wait_number += 1
            self.waiting_queue.append((wait_number, count))
            self._update_waiting_notice()
            self._reset_selection()
            self._refresh(
                f'受付番号{wait_number}番でお待ちください。'
                f'現在の残り席数は{remaining}席です。'
            )
            return

        self.party_sizes.append(count)
        messages = []
        for ticket in range(1, count + 1):
            if ticket >= 5 and (ticket - 5) % 5 == 0:
                messages.append(
                    f'番号札{ticket}番の方は、大変申し訳ございませんが、'
                    '席をくっつけてご利用ください。'
                )
            else:
                messages.append(f'番号札{ticket}番の方は、お進みください。')
        self.occupied += count
        self._reset_selection()
        self._refresh('\n'.join(messages))

    def _leave(self):
        count = self._selected_count()
        if count is None:
            return
        if count > self.occupied:
            self._refresh(f'現在の利用人数は{self.occupied}人です。人数を確認してください。')
            return
        self.occupied -= count
        self._reset_selection()
        self._refresh(f'{count}人の退店を登録しました。')

    def _call_waiting(self):
        if not self.waiting_queue:
            self._refresh('待っている組はいません。')
            return

        called_numbers = []
        messages = []
        while self.waiting_queue:
            wait_number, party_size = self.waiting_queue[0]
            if party_size > self.capacity - self.occupied:
                break
            self.waiting_queue.pop(0)
            self.occupied += party_size
            called_numbers.append(wait_number)
            messages.append(
                f'受付番号{wait_number}番の方、席が空きました。お進みください。'
            )
        if called_numbers:
            numbers_text = '、'.join(f'{number}番' for number in called_numbers)
            self.called_number_label.config(text=numbers_text)
            self._update_waiting_notice()
            self._refresh('\n'.join(messages))
            threading.Thread(
                target=self._announce_called_numbers,
                args=(called_numbers,),
                daemon=True,
            ).start()
        else:
            self._refresh('空席が足りないため、まだ呼び出せません。')

    def _announce_called_numbers(self, numbers):
        winsound.Beep(660, 300)
        winsound.Beep(880, 450)
        number_text = '、'.join(
            f'{self._number_to_hiragana(number)}ばん' for number in numbers
        )
        announcement = f'{number_text}でおまちのかた、ごあんないします。'
        encoded_text = base64.b64encode(
            announcement.encode('utf-16le')
        ).decode('ascii')
        encoded_voice_name = base64.b64encode(
            ANNOUNCEMENT_VOICE_NAME.encode('utf-16le')
        ).decode('ascii')
        powershell_script = (
            'Add-Type -AssemblyName System.Speech; '
            f"$text = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{encoded_text}')); "
            f"$voiceName = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{encoded_voice_name}')); "
            '$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
            '$voices = $speaker.GetInstalledVoices(); '
            "$voice = $voices | Where-Object { $_.VoiceInfo.Culture.Name -eq 'ja-JP' -and $_.VoiceInfo.Name -eq $voiceName } | Select-Object -First 1; "
            "if (-not $voice) { $voice = $voices | Where-Object { $_.VoiceInfo.Culture.Name -eq 'ja-JP' } | Select-Object -First 1 }; "
            'if ($voice) { $speaker.SelectVoice($voice.VoiceInfo.Name); '
            f'$speaker.Rate = {ANNOUNCEMENT_RATE}; $speaker.Speak($text) }}'
        )
        try:
            subprocess.Popen(
                ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', powershell_script],
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
        except OSError:
            pass

    def _number_to_hiragana(self, number):
        digit_names = ('ぜろ', 'いち', 'に', 'さん', 'よん', 'ご', 'ろく', 'なな', 'はち', 'きゅう')
        if number >= 10000:
            return ''.join(digit_names[int(digit)] for digit in str(number))

        reading = ''
        thousands = number // 1000
        hundreds = (number // 100) % 10
        tens = (number // 10) % 10
        ones = number % 10

        if thousands:
            if thousands == 1:
                reading += 'せん'
            elif thousands == 3:
                reading += 'さんぜん'
            elif thousands == 8:
                reading += 'はっせん'
            else:
                reading += digit_names[thousands] + 'せん'

        if hundreds:
            hundreds_readings = {
                1: 'ひゃく', 2: 'にひゃく', 3: 'さんびゃく',
                4: 'よんひゃく', 5: 'ごひゃく', 6: 'ろっぴゃく',
                7: 'ななひゃく', 8: 'はっぴゃく', 9: 'きゅうひゃく',
            }
            reading += hundreds_readings[hundreds]

        if tens:
            reading += 'じゅう' if tens == 1 else digit_names[tens] + 'じゅう'
        if ones:
            reading += digit_names[ones]
        return reading or 'ぜろ'

    def _refresh(self, message):
        remaining = self.capacity - self.occupied
        self.remaining_label.config(text=f'残り {remaining} / {self.capacity} 席')
        self.waiting_label.config(text=f'待ち組数 {len(self.waiting_queue)}組')
        self.status_label.config(text='満席です。' if remaining == 0 else '')
        self.log.config(state='normal')
        self.log.insert('end', message + '\n')
        self.log.see('end')
        self.log.config(state='disabled')


root = tk.Tk()
app = SeatCounterApp(root)
root.mainloop()