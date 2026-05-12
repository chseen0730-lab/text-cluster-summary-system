Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "D:\软件著作权\软著项目\网络文本观点聚类与摘要辅助分析系统\frontend"
objShell.Run "cmd /k ""node_modules\.bin\vite.cmd""", 1, False
