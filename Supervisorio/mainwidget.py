from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, MotorPopup, DataGraphPopup, HistGraphPopup, DataGraphVZPopup, SetPointPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
import random
from timeseriesgraph import TimeSeriesGraph
from bdhandler import BDHandler
from kivy_garden.graph import LinePlot
from threading import Lock


class MainWidget(BoxLayout):
    """
    Widget principal
    """
    _updateThread = None
    _updateWidgets = True
    _tags = {}
    _max_points = 20

    def __init__(self, **kwargs):
        """
        Construtor do Widget Principal
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._setPoint = kwargs.get('scan_time')
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._scanPopup = ScanPopup(self._scan_time)
        self._motorConfig = MotorPopup()
        self._setpointConfig = SetPointPopup()
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)
        self._lock = Lock()
        self._connected = False
        self._motorState = False
        self._solenoidesStates = [False,False,False]
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        for key,value in kwargs.get('modbus_addrs').items():
            plot_color = (random.random(), random.random(), random.random(), 1)
            self._tags[key] = {'addr': value['addr'], 'table': value['table'], 'color': plot_color, 'multiplicador': value['multiplicador']}

        self._nGraph = DataGraphPopup(self._max_points, self._tags['nivel']['color'])
        self._vGraph = DataGraphVZPopup(self._max_points, self._tags['vz_entrada']['color'])
        self._hgraph = HistGraphPopup(tags=self._tags)
        self._db = BDHandler(kwargs.get('db_path'),self._tags)

    def startDataRead(self,ip,port):
        """
        Método utilizado para a configuração do IP e porta do servidor MODBUS e inicializa uma thread para leitura de dados e atualização da interface
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.client = self._serverPort
        try:
            Window.set_system_cursor("wait")
            self._modbusClient.open()

            self._readModbus = {
                'coil': self._modbusClient.read_coils,
                'h_reg': self._modbusClient.read_holding_registers,
                'i_reg': self._modbusClient.read_input_registers,
                'd_inputs': self._modbusClient.read_discrete_inputs
            }

            Window.set_system_cursor("arrow")
            if(self._modbusClient.is_open):
                self._updateThread = Thread(target=self.updater)
                self._updateThread.start()
                self._connected = True
                self.ids.img_con.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor")
        except Exception as e:
            print("Error: é aqui",e.args)
    
    def updater(self):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface e inserção dos dados no Banco de dados
        """
        try:
            while self._updateWidgets:
                self.readData()
                self.updateGUI()
                self.levelController()
                self._db.insertData(self._meas)
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Error: ",e.args)

    def readData(self):
        """
        Método para a leitura de dados por meio do protocolo MODBUS
        """
        self._meas['timestamp'] = datetime.now()
        
        for key,value in self._tags.items():
            self._lock.acquire()
            if(self._tags[key]['multiplicador'] is None):
                self._meas['values'][key] = self._readModbus[self._tags[key]['table']](self._tags[key]['addr'])[0]
            else:
                self._meas['values'][key] = self._readModbus[self._tags[key]['table']](self._tags[key]['addr'])[0] / self._tags[key]['multiplicador']
            print(key, self._meas['values'][key])
            self._lock.release()

    def updateGUI(self): 
        """
        Método para atualização da interface a partir dos novos dados lidos
        """

        keysToUpdate = ('temp_estator', 'freq_mot', 'tensao', 'rotacao', 'pot_entrada', 'corrente','nivel','vz_entrada')
        for key in keysToUpdate:
            if key == 'nivel_l' or key == 'nivel_h':
                print(self._meas['values'][key])
            else:
                self.ids[key].text = str(self._meas['values'][key] )

        #Atualização do nível do reservatorio
        self.ids.lb_res.size = (self.ids.lb_res.size[0],self._meas['values']['nivel']/750*self.ids.reservatorio.size[1])
        self.ids.lb_vz.size = (self.ids.lb_vz.size[0],self._meas['values']['vz_entrada']/8.4*self.ids.vazao.size[1])

        #Atualização do gráfico
        self._nGraph.ids.nGraph.updateGraph((self._meas['timestamp'],self._meas['values']['nivel']),0) 
        self._vGraph.ids.vGraph.updateGraph((self._meas['timestamp'],self._meas['values']['vz_entrada']),0)

    def stopRefresh(self):
        self._updateWidgets = False

    def levelController(self):
        print(self._meas['values']['nivel'])
        self._setPoint

    def motorController(self):
        if self._connected:
            self._lock.acquire()
            if not self._motorState:
                self._motorState = True
                self._modbusClient.write_single_coil(800,1)
                self.ids.motor.background_color = (0, 1, 0, 1)
                self.ids.motor.text = "Desliga"
                print('ligou')
            else:
                self._motorStafrom kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, MotorPopup, DataGraphPopup, HistGraphPopup, DataGraphVZPopup, SetPointPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
import random
from timeseriesgraph import TimeSeriesGraph
from bdhandler import BDHandler
from kivy_garden.graph import LinePlot
from threading import Lock


class MainWidget(BoxLayout):
    """
    Widget principal
    """
    _updateThread = None
    _updateWidgets = True
    _tags = {}
    _max_points = 20

    def __init__(self, **kwargs):
        """
        Construtor do Widget Principal
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._setPoint = kwargs.get('scan_time')
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._scanPopup = ScanPopup(self._scan_time)
        self._motorConfig = MotorPopup()
        self._setpointConfig = SetPointPopup()
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)
        self._lock = Lock()
        self._connected = False
        self._motorState = False
        self._solenoidesStates = [False,False,False]
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        for key,value in kwargs.get('modbus_addrs').items():
            plot_color = (random.random(), random.random(), random.random(), 1)
            self._tags[key] = {'addr': value['addr'], 'table': value['table'], 'color': plot_color, 'multiplicador': value['multiplicador']}

        self._nGraph = DataGraphPopup(self._max_points, self._tags['nivel']['color'])
        self._vGraph = DataGraphVZPopup(self._max_points, self._tags['vz_entrada']['color'])
        self._hgraph = HistGraphPopup(tags=self._tags)
        self._db = BDHandler(kwargs.get('db_path'),self._tags)

    def startDataRead(self,ip,port):
        """
        Método utilizado para a configuração do IP e porta do servidor MODBUS e inicializa uma thread para leitura de dados e atualização da interface
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.client = self._serverPort
        try:
            Window.set_system_cursor("wait")
            self._modbusClient.open()

            self._readModbus = {
                'coil': self._modbusClient.read_coils,
                'h_reg': self._modbusClient.read_holding_registers,
                'i_reg': self._modbusClient.read_input_registers,
                'd_inputs': self._modbusClient.read_discrete_inputs
            }

            Window.set_system_cursor("arrow")
            if(self._modbusClient.is_open):
                self._updateThread = Thread(target=self.updater)
                self._updateThread.start()
                self._connected = True
                self.ids.img_con.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor")
        except Exception as e:
            print("Error: é aqui",e.args)
    
    def updater(self):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface e inserção dos dados no Banco de dados
        """
        try:
            while self._updateWidgets:
                self.readData()
                self.updateGUI()
                self.levelController()
                self._db.insertData(self._meas)
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Error: ",e.args)

    def readData(self):
        """
        Método para a leitura de dados por meio do protocolo MODBUS
        """
        self._meas['timestamp'] = datetime.now()
        
        for key,value in self._tags.items():
            self._lock.acquire()
            if(self._tags[key]['multiplicador'] is None):
                self._meas['values'][key] = self._readModbus[self._tags[key]['table']](self._tags[key]['addr'])[0]
            else:
                self._meas['values'][key] = self._readModbus[self._tags[key]['table']](self._tags[key]['addr'])[0] / self._tags[key]['multiplicador']
            print(key, self._meas['values'][key])
            self._lock.release()

    def updateGUI(self): 
        """
        Método para atualização da interface a partir dos novos dados lidos
        """

        keysToUpdate = ('temp_estator', 'freq_mot', 'tensao', 'rotacao', 'pot_entrada', 'corrente','nivel','vz_entrada')
        for key in keysToUpdate:
            if key == 'nivel_l' or key == 'nivel_h':
                print(self._meas['values'][key])
            else:
                self.ids[key].text = str(self._meas['values'][key] )

        #Atualização do nível do reservatorio
        self.ids.lb_res.size = (self.ids.lb_res.size[0],self._meas['values']['nivel']/750*self.ids.reservatorio.size[1])
        self.ids.lb_vz.size = (self.ids.lb_vz.size[0],self._meas['values']['vz_entrada']/8.4*self.ids.vazao.size[1])

        #Atualização do gráfico
        self._nGraph.ids.nGraph.updateGraph((self._meas['timestamp'],self._meas['values']['nivel']),0) 
        self._vGraph.ids.vGraph.updateGraph((self._meas['timestamp'],self._meas['values']['vz_entrada']),0)

    def stopRefresh(self):
        self._updateWidgets = False

    def levelController(self):
        print(self._meas['values']['nivel'])
        self._setPoint

    def motorController(self):
        if self._connected:
            self._lock.acquire()
            if not self._motorState:
                self._motorState = True
                self._modbusClient.write_single_coil(800,1)
                self.ids.motor.background_color = (0, 1, 0, 1)
                self.ids.motor.text = "Desliga"
                print('ligou')
            else:
                self._motorState = False
                self._modbusClient.write_single_coil(800,0)
                self.ids.motor.background_color = (0.5, 0.5, 0.5, 1)
                self.ids.motor.text = "Liga"
                print('desligou')
            self._lock.release()
        else:
            print("Conecte primeiro")

    def setFreq(self, freq, t_part):
        try:
            if self._connected:
                sendableFreq = int(freq)*1
                sendableTime = int(t_part)*10
                self._modbusClient.write_single_register(799,sendableFreq)
                self._modbusClient.write_single_register(798,sendableTime)
            else:
                print("Conecte primeiro")
        except Exception as e:
            print(e)
        
    def solenoideController(self, num, button):
        print('entrou')
        if self._connected:
            self._lock.acquire()
            if not self._solenoidesStates[num-1]:
                self._solenoidesStates[num-1] = True
                addr = 800 + num
                sId = "solenoide_"+str(num)
                button.text = "Desativar"
                self._modbusClient.write_single_coil(addr,1)
                print('ligou')
                if sId == 'solenoide_1':
                    self.ids.sol1.opacity = 1
                if sId == 'solenoide_2':
                    self.ids.sol2.opacity = 1
                if sId == 'solenoide_3':
                    self.ids.sol3.opacity = 1

            else:
                self._solenoidesStates[num-1] = False
                addr = 800 + num
                sId = "solenoide_"+str(num)
                print(sId,addr)
                button.text = "Ativar"
                self._modbusClient.write_single_coil(addr,0)
                print('deligou '+sId)
                if sId == 'solenoide_1':
                    self.ids.sol1.opacity = 0
                if sId == 'solenoide_2':
                    self.ids.sol2.opacity = 0
                if sId == 'solenoide_3':
                    self.ids.sol3.opacity = 0
            self._lock.release()
        else:
            print("Conecte primeiro")
        


    def getDataDB(self):
        """
        Método que coleta as informações da interface fornecida pelo usuário e requisita a busca no BD
        """
        try:
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text)
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)
            cols = []
            for sensor in self._hgraph.ids.sensores.children:
                if(sensor.ids.checkbox.active):
                    cols.append(sensor.id)

            if init_t is None or final_t is None or len(cols)==0:
                return
            
            cols.append('timestamp')
            
            dados = self._db.selectData(cols, init_t, final_t)
            if dados is None or len(dados['timestamp'])==0:
                return
            
            self._hgraph.ids.graph.clearPlots()

            for key,value in dados.items():
                if key == 'timestamp':
                    continue
                p = LinePlot(line_width=1.5, color=self._tags[key]['color'])
                p.points = [(x,value[x]) for x in range(0,len(value))]
                self._hgraph.ids.graph.add_plot(p)
            self._hgraph.ids.graph.xmax = len(dados[cols[0]])
            self._hgraph.ids.graph.update_x_labels([datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") for x in dados['timestamp']])
        except Exception as e:
            print("Erro: ",e.args)

    def parseDTString(self, datetime_str):
        """
        Método que converte a string inserida pelo usuário para o formato utilizado pelo BD
        """
        try:
            d = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            return d.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Erro:4 ",e.args) 




        

    
