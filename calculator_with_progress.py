以下のコードは、Tkinterを使用した簡単な電卓アプリケーションです。このコードには数字ボタン、演算子ボタン、イコールボタン、クリアボタン、小数点ボタンなどが含まれており、表示画面に結果を表示し、エラー処理も実装されています。

```python
import tkinter as tk

class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("電卓アプリ")
        self.entry_value = ""

        # 表示画面の作成
        self.display_label = tk.Label(self.window, text="", width=20, borderwidth=5)
        self.display_label.grid(row=0, column=0, columnspan=4)

        # 数字ボタンの作成
        buttons = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            '0', '.', '='
        ]

        row_val = 1
        col_val = 0

        for button in buttons:
            tk.Button(self.window, text=button, width=10, command=lambda button=button: self.click_button(button)).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 2:
                col_val = 0
                row_val += 1

        # 演算子ボタンの作成
        tk.Button(self.window, text="+", width=10, command=lambda: self.click_button("+")).grid(row=row_val, column=0)
        tk.Button(self.window, text="-", width=10, command=lambda: self.click_button("-")).grid(row=row_val, column=1)
        tk.Button(self.window, text="*", width=10, command=lambda: self.click_button("*")).grid(row=row_val, column=2)
        tk.Button(self.window, text="/", width=10, command=lambda: self.click_button("/")).grid(row=row_val, column=3)

        # クリアボタンの作成
        tk.Button(self.window, text="C", width=21, command=self.clear_entry).grid(row=row_val+1, column=0, columnspan=4)

    def click_button(self, button):
        if button == "=":
            try:
                result = str(eval(self.entry_value))
                self.display_label['text'] = result
                self.entry_value = ""
            except Exception as e:
                self.display_label['text'] = "エラー"
                self.entry_value = ""
        elif button == "C":
            self.clear_entry()
        else:
            if self.entry_value == "" or self.entry_value == "0" and button != ".":
                self.entry_value += str(button)
            else:
                self.entry_value += button
            self.display_label['text'] = self.entry_value

    def clear_entry(self):
        self.entry_value = ""
        self.display_label['text'] = ""

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
```

このコードはTkinterライブラリを使用してGUIを作成しています。calculator.pyというファイルに保存してください。

このアプリケーションでは、数字ボタンをクリックすると入力欄に値が追加されます。また、演算子ボタンをクリックすると入力された値に対応する演算を行います。「=」ボタンをクリックすると、入力された値に対して演算が実行され、その結果が表示画面に表示されます。「C」ボタンをクリックすると、入力欄がクリアされます。

このアプリケーションではエラー処理も実装されており、計算ミスによって生じるエラーは「エラー」というテキストで表現されます。