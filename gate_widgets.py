"""Responsive layout helpers for the existing Tk/ttk interface."""
import tkinter as tk
from tkinter import ttk


def install_flow_rows(root):
    """Wrap horizontal control rows; leave text, lists and scroll holders alone."""
    allowed = (ttk.Button, ttk.Menubutton, ttk.Label, ttk.Entry, ttk.Combobox, ttk.Checkbutton)
    for frame in root.winfo_children():
        install_flow_rows(frame)
        children = frame.winfo_children()
        if not isinstance(frame, ttk.Frame) or len(children) < 3 or not all(isinstance(c, allowed) for c in children):
            continue
        if not all(c.winfo_manager() == 'pack' and c.pack_info().get('side') in {'left', 'right'} for c in children):
            continue
        for child in children:
            child.pack_forget()
            child._flow_hidden = False
        state = {'width': None, 'columns': 0}
        def reflow(event=None, frame=frame, children=children, state=state):
            width = frame.winfo_width()
            if width < 50 or state['width'] == width:
                return
            state['width'] = width
            for col in range(state['columns']):
                frame.columnconfigure(col, weight=0)
            row = col = used = 0
            for child in children:
                if child._flow_hidden:
                    child.grid_remove()
                    continue
                requested = min(width - 12, child.winfo_reqwidth() + 12)
                if used and used + requested > width:
                    row += 1; col = used = 0
                child.grid(row=row, column=col, sticky='ew', padx=3, pady=3)
                if isinstance(child, ttk.Entry) and not isinstance(child, ttk.Combobox):
                    frame.columnconfigure(col, weight=1)
                used += requested; col += 1
                state['columns'] = max(state['columns'], col)
        frame.bind('<Configure>', reflow, add='+')
        def refresh(state=state, reflow=reflow):
            state['width'] = None
            reflow()
        frame._flow_refresh = refresh
        frame.after_idle(reflow)


def adapt_wraplength(root, width):
    for child in root.winfo_children():
        if isinstance(child, ttk.Label):
            try:
                if int(child.cget('wraplength')) > 0:
                    available = min(width, root.winfo_width()) if root.winfo_width() > 50 else width
                    child.configure(wraplength=max(160, available - 32))
            except (ValueError, tk.TclError):
                pass
        adapt_wraplength(child, width)
