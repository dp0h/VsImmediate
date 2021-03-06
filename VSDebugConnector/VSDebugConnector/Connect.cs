using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Windows.Forms;
using Extensibility;
using EnvDTE;
using EnvDTE80;
using System.Text;

namespace VSDebugConnector
{
    /// <summary>The object for implementing an Add-in.</summary>
    /// <seealso class='IDTExtensibility2' />
    public class Connect : IDTExtensibility2
    {
        /// <summary>Implements the constructor for the Add-in object. Place your initialization code within this method.</summary>
        public Connect()
        {
        }

        private const string PortFileName = "vsdbg.port";

        /// <summary>Implements the OnConnection method of the IDTExtensibility2 interface. Receives notification that the Add-in is being loaded.</summary>
        /// <param term='application'>Root object of the host application.</param>
        /// <param term='connectMode'>Describes how the Add-in is being loaded.</param>
        /// <param term='addInInst'>Object representing this Add-in.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnConnection(object application, ext_ConnectMode connectMode, object addInInst, ref Array custom)
        {
            _applicationObject = (DTE2)application;
            _addInInstance = (AddIn)addInInst;

            _encoder = new ASCIIEncoding();
            _listener = new TcpListener(IPAddress.Any, 0);
            _stop = new ManualResetEvent(false);
            _thread = new System.Threading.Thread(ProcessClients);
            _listener.Start();
            _thread.Start();

            var port = ((IPEndPoint) _listener.LocalEndpoint).Port;
            //MessageBox.Show(string.Format("Port: {0}", port), "Port", MessageBoxButtons.OK, MessageBoxIcon.Information);
            File.WriteAllText(Path.Combine(Environment.GetEnvironmentVariable("TEMP"), PortFileName), port.ToString());
        }

        /// <summary>Implements the OnDisconnection method of the IDTExtensibility2 interface. Receives notification that the Add-in is being unloaded.</summary>
        /// <param term='disconnectMode'>Describes how the Add-in is being unloaded.</param>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnDisconnection(ext_DisconnectMode disconnectMode, ref Array custom)
        {
            _listener.Stop();
            _stop.Set();
            _thread.Join();
            try {
                File.Delete(Path.Combine(Environment.GetEnvironmentVariable("TEMP"), PortFileName));
            } catch(IOException) {}
        }

        /// <summary>Implements the OnAddInsUpdate method of the IDTExtensibility2 interface. Receives notification when the collection of Add-ins has changed.</summary>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnAddInsUpdate(ref Array custom)
        {
        }

        /// <summary>Implements the OnStartupComplete method of the IDTExtensibility2 interface. Receives notification that the host application has completed loading.</summary>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnStartupComplete(ref Array custom)
        {
        }

        /// <summary>Implements the OnBeginShutdown method of the IDTExtensibility2 interface. Receives notification that the host application is being unloaded.</summary>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnBeginShutdown(ref Array custom)
        {
        }

        /// <summary>
        /// Delimiter in communication protocol
        /// </summary>
        private const char BEL = '\x07';

        /// <summary>
        /// Request types
        /// </summary>
        private enum ReqType {
            Unknown = 0,
            Value = 1,
            Type = 2,
            Members = 3,
            All = 4
        }

        /// <summary>
        /// Response types
        /// </summary>
        private enum RespType {
            Unknown = 0,
            Error = 1,
            Value = 2,
            Array = 3
        }

        /// <summary>
        /// Thread function which handles TCP requests
        /// </summary>
        private void ProcessClients() {
            var buff = new byte[4096];

            while (!_stop.WaitOne(0)) {
                try {
                    var client = _listener.AcceptSocket();
                    var bytesReacived = client.Receive(buff);
                    if (bytesReacived > 0) {
                        var cmd = _encoder.GetString(buff, 0, bytesReacived);
                        var type = ReqType.Unknown;
                        string expr = null;

                        var items = cmd.Split(BEL);
                        if (items.Length == 2) {
                            type = (ReqType)int.Parse(items[0]);
                            expr = items[1];
                        }

                        if (items.Length != 2 || type == ReqType.Unknown || string.IsNullOrEmpty(expr)) {
                            client.Send(FormatMessage(RespType.Error, "Invalid input"));
                        } else {
                            client.Send(ProcessExpression(type, expr));
                        }
                    }
                    client.Close();
                } catch (SocketException) { }
            }
        }

        private byte[] FormatMessage(RespType type, string message) {
            return _encoder.GetBytes(string.Format("{0}{1}{2}", (int) type, BEL, message));
        }

        private byte[] ProcessExpression(ReqType type, string expression) {
            if (!IsInDebugMode(_applicationObject)) {
                return FormatMessage(RespType.Error, "Not in debug mode");
            }

            Expression expr = null;
            try {
                expr = _applicationObject.Debugger.GetExpression(expression);
            } catch (System.Runtime.InteropServices.COMException) { }

            if (expr == null || !expr.IsValidValue) {
                return FormatMessage(RespType.Error, string.Format("Couldn't evaluate expression: {0}", expression));
            }

            switch (type) {
                case ReqType.Value:
                    return FormatMessage(RespType.Value, expr.Value);
                case ReqType.Type:
                    return FormatMessage(RespType.Value, expr.Type);
                case ReqType.Members: {
                    var memb = new List<string>();
                    foreach (Expression c in expr.DataMembers) {
                        memb.Add(c.Name);
                    }
                    return FormatMessage(RespType.Array, string.Join("" + BEL, memb));
                }
                case ReqType.All: {
                    var sb = new StringBuilder(expr.Value);
                    foreach (Expression c in expr.DataMembers) {
                        sb.Append(string.Format("\n\t{0}: {1}", c.Name, c.Value));
                    }
                    return FormatMessage(RespType.Value, sb.ToString());
                }
            }
            return FormatMessage(RespType.Error, "Internal error");
        }

        /// <summary>
        /// Checks if VS in Debug mode
        /// </summary>
        /// <param name="dte"></param>
        /// <returns></returns>
        private bool IsInDebugMode(DTE2 dte) {
            if (dte == null || dte.Debugger == null)
                return false;
            return dte.Debugger.CurrentMode == dbgDebugMode.dbgBreakMode;
        }

        private DTE2 _applicationObject;
        private AddIn _addInInstance;
        private ASCIIEncoding _encoder;
        private TcpListener _listener;
        private System.Threading.Thread _thread;
        private ManualResetEvent _stop;
    }
}