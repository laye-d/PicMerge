import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

#get path no matter running from Python or an exe file
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class PicMerge(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("PicMerge APP")
        # self.iconbitmap(r"C:\x\PicMerge\LL.ico")
        self.iconbitmap(resource_path(r'.\LL.ico'))
        

        #默认行列数
        rows = 2
        columns = 3

        # 创建行数输入框
        self.rows_label = tk.Label(self, text="Rows:")
        self.rows_label.grid(row=0, column=0, padx=5, pady=1)
        self.rows_entry = tk.Entry(self)
        self.rows_entry.grid(row=0, column=1, padx=5, pady=1)
        self.rows_entry.insert(0, rows)
        
        # 创建列数输入框
        self.columns_label = tk.Label(self, text="Columns:")
        self.columns_label.grid(row=1, column=0, padx=5, pady=1)
        self.columns_entry = tk.Entry(self)
        self.columns_entry.grid(row=1, column=1, padx=5, pady=1)
        self.columns_entry.insert(0, columns)
        
        # 创建设置按钮
        self.set_button = tk.Button(self, text="Set Grid", command=self.set_grid)
        self.set_button.grid(row=1, column=2, padx=5, pady=1) #columnspan=2, 

        

        # 创建Padding输入框
        self.padding_label = tk.Label(self, text="Grid Padding:")
        self.padding_label.grid(row=2, column=0, padx=5, pady=1)
        self.padding_entry = tk.Entry(self)
        self.padding_entry.grid(row=2, column=1, padx=5, pady=1)
        self.padding_entry.insert(0, 0)# 默认格子间距（第二个2参数）
        grid_padding =  self.padding_entry.get() 

        # 保存按钮
        self.save_button = tk.Button(self, text="Save Merged Picture", command=self.save_image)
        self.save_button.grid(row=2, column=2,  pady=10) #columnspan=2, 
        



        # 宫格的格子列表
        self.grid_cells = []

        # 创建宫格
        for i in range(rows):
            for j in range(columns):
                cell = tk.Frame(self, width=200, height=200, relief=tk.RAISED, borderwidth=2)
                cell.grid(row=i+3, column=j+3, padx=grid_padding, pady=grid_padding)
                self.grid_cells.append(cell)

                # 为每个格子添加点击事件
                cell.bind("<Button-1>", lambda event, index=i * columns + j: self.select_image(index))
                cell.bind("<Button-3>", lambda event, index=i * columns + j: self.clear_image(index))

        #按默认行列数刷新宫格
        self.set_grid()



        # 用于存储选择的图片的路径
        self.image_paths = [None] * (rows*columns)

    def set_grid(self):
        rows = int(self.rows_entry.get())
        columns = int(self.columns_entry.get())
        self.rows = rows
        self.columns = columns
        self.create_grid()

    def create_grid(self):
        # 清除之前的格子
        for cell in self.grid_cells:
            cell.destroy()
        self.grid_cells = []
        rows = int(self.rows_entry.get())
        columns = int(self.columns_entry.get())
        self.image_paths = [None] * (rows*columns)
        

        grid_padding =  self.padding_entry.get() 

        # 创建新的宫格
        for i in range(self.rows):
            for j in range(self.columns):
                cell = tk.Frame(self, width=200, height=200, relief=tk.RAISED, borderwidth=2)
                cell.grid(row=i+3, column=j, padx=grid_padding, pady=grid_padding)
                self.grid_cells.append(cell)
                
                # 为每个格子添加点击事件
                cell.bind("<Button-1>", lambda event, index=i * self.columns + j: self.select_image(index))#左键选择新图片
                cell.bind("<Button-3>", lambda event, index=i * columns + j: self.clear_image(index))#右键删除图片
    def select_image(self, index):
        from tkinter.filedialog import askopenfilename
        # 清除格子中的旧图片
        self.clear_image(index)

        # 弹出文件选择对话框
        filename = askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])

        if filename:

            
            # 打开图像并进行预览
            image = Image.open(filename)
            image.thumbnail((180, 180))  # 缩放图像以适应格子大小
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.grid_cells[index], image=photo)
            label.image = photo
            label.pack()
            # 绑定点击事件
            label.bind("<Button-1>", lambda event, index=index: self.select_image(index))
            label.bind("<Button-3>", lambda event, index=index: self.clear_image(index))

            # 保存图片路径
            self.image_paths[index] = filename


    def clear_image(self, index):         
        # 清除格子中的图片
        for widget in self.grid_cells[index].winfo_children():
            widget.destroy()
        self.image_paths[index] = None

    def save_image(self):
        from tkinter.filedialog import asksaveasfilename

        grid_padding =  int(self.padding_entry.get())

        # 弹出保存文件对话框
        filename = asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])

        if filename:
            # 检查是否有足够的图片路径来进行拼接
            if all(path is not None for path in self.image_paths):
                target_width = 0
                target_height = 0
                for i, path in enumerate(self.image_paths):
                    if Image.open(path).height > target_height:
                        target_height = Image.open(path).height
                    if Image.open(path).width > target_width:
                        target_width = Image.open(path).width


                    

                # 计算拼接后图片的尺寸
                rows = int(self.rows_entry.get())
                columns = int(self.columns_entry.get())
                
                grid_width = columns * target_width + (columns +1) * grid_padding
                grid_height = rows * target_height + (rows+1) * grid_padding
                result_image = Image.new("RGB", (grid_width, grid_height))
                

                # 拼接图片
                x_offset = grid_padding
                y_offset = grid_padding
                for i, path in enumerate(self.image_paths):
                    image = Image.open(path)
                    
                    image.thumbnail((target_width, target_height))
                    result_image.paste(image, (x_offset, y_offset))

                    x_offset += target_width + grid_padding
                    if (i + 1) % columns == 0:
                        x_offset = grid_padding
                        y_offset += target_height + grid_padding

                # 保存拼接后的图片
                result_image.save(filename)
                messagebox.showinfo("Image Saved", "The image has been saved successfully!")
            else:
                messagebox.showwarning("Missing Images", "Please select images for all grid cells.")

    def run(self):
        self.mainloop()

if __name__ == "__main__":

    app = PicMerge()

    app.run()

