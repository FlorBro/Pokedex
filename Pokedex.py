import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import os
from pathlib import Path
import json
import requests
class MyWidget(QMainWindow):
    def __init__(self):
        global current_working_directory
        current_working_directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__()
        self.widget_contenu = QWidget()
        # Configuration de la fenêtre
        self.setWindowTitle("Pokedex")
        self.setGeometry(460, 240, 500, 300)
        self.setMaximumSize(QSize(1000,1000))
        self.main_layout =QVBoxLayout(self.widget_contenu)
        # Layout principal
        self.group_layout = QHBoxLayout()
        self.labelValuelist={}
        self.buttonlist={}
        self.numlist={}  
        self.keepPixmap={}
        ###
        self.search_layout=QHBoxLayout()
        self.searchBar= QLineEdit()
        self.searchBar.setPlaceholderText("Search Pokemon by name/n° ...")
        self.searchBar.setFixedWidth(150)
        self.searchButton= QPushButton('◓')
        self.searchButton.setFixedWidth(20)
        self.searchButton.clicked.connect(self.search)
        self.CancelButton = QPushButton('🗙')
        self.CancelButton.setFixedWidth(20)
        self.CancelButton.clicked.connect(self.cancelsearch)
        self.search_layout.addWidget(self.searchBar)
        self.search_layout.addWidget(self.searchButton)
        self.search_layout.addWidget(self.CancelButton)
        self.main_layout.addLayout(self.search_layout)
        with open(f"{current_working_directory}\\Pokedex_descriptif.json",'r',encoding='utf-8') as file:
            self.data = json.load(file)
        self.number = 1  # Initialisation en dehors de la boucle
        self.total = 0
        for test in self.data:
            if test != "GlobalType":
                self.total +=1
                if self.number <=9:
                    pokemonwidget = self.Pokemon_widget(self.data,test,self.number,False)
                    self.group_layout.addWidget(pokemonwidget)
                    if self.number %3==0:
                        self.main_layout.addLayout(self.group_layout)
                        self.group_layout = QHBoxLayout()
                self.number += 1  # Incrémentation pour passer au Pokémon suivant
        if self.number % 3 != 1:
            self.main_layout.addLayout(self.group_layout)
        self.main_layout.addWidget(self.widget_contenu)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.widget_contenu)  # Ajouter le contenu
        scroll_area.setWidgetResizable(True)  # Ajuster la taille du contenu
        self.setCentralWidget(scroll_area)
        self.LoadButton= QPushButton('Charger plus')
        self.LoadButton.setFixedWidth(150)
        self.LoadButton.clicked.connect(self.load)
        self.main_layout.addWidget(self.LoadButton)    
        
    def load(self):
        self.count = 0
        self.main_layout.removeWidget(self.LoadButton)
        self.LoadButton.hide()
        for child in self.widget_contenu.findChildren(QLabel):  # Parcours des QLabel
            if child.pixmap() is not None:  # Vérifie si un pixmap est défini
                self.count += 1
        self.number=int((self.count/2) + 1)
        for test in self.data:
            if test != "GlobalType":
                tag = int(test.split('#')[1])
                if tag >=(int(self.count/2)+1):
                    if tag <=(self.count/2)+9:
                        pokemonwidget = self.Pokemon_widget(self.data,f"#{tag}",self.number,False)
                        self.group_layout.addWidget(pokemonwidget)
                        if self.number %3==0:
                            self.main_layout.addLayout(self.group_layout)
                            self.group_layout = QHBoxLayout()
                        self.number += 1  # Incrémentation pour passer au Pokémon suivant
        if self.number % 3 != 1:
            self.main_layout.addLayout(self.group_layout)
       
        if (self.count/2)+9 < self.total:
            self.LoadButton= QPushButton('Charger plus')
            self.LoadButton.setFixedWidth(150)
            self.LoadButton.clicked.connect(self.load)
            self.main_layout.addWidget(self.LoadButton)
    def cancelsearch(self):
        if hasattr(self, "searchwidget") and self.searchwidget is not None:
            self.main_layout.removeWidget(self.searchwidget)
            self.searchwidget.deleteLater()
            self.searchwidget = None
        self.LoadButton.show()
        try : 
            for list in self.listdexception:
                self.labelValuelist[list].show()
                self.buttonlist[list].show()
                self.numlist[list].show()
        except:pass
        self.searchBar.clear()
    def search(self):
        self.listdexception=[]
        self.PokeSearch = self.searchBar.text().strip()
        global PokeNumber
        #recherche par Nom
        if "#" not in self.PokeSearch and self.PokeSearch is not None :
            for parent_key, nested_dict in self.data.items():
                if isinstance(nested_dict, dict) and self.PokeSearch in nested_dict.values():
                    Tagtest = parent_key
                    PokeNumber=Tagtest
        #recherche par tag
        else :  
            PokeNumber=self.PokeSearch
        #liste des pokemons dispo
        for Numberexception in self.data:
            if Numberexception!='GlobalType':
                self.listdexception.append(Numberexception)
                
        #supprime le pokemon affiché lors de la recherche 
        if hasattr(self, "searchwidget") and self.searchwidget is not None:
            self.main_layout.removeWidget(self.searchwidget)
            self.searchwidget.deleteLater()
            self.searchwidget = None
        ##disparition
        if self.PokeSearch is not None:
            for list in self.listdexception:   ####List dexeception prend la totalité des widgets
                try:
                    self.labelValuelist[list].hide()
                    self.buttonlist[list].hide()
                    self.numlist[list].hide()
                except : pass
            self.LoadButton.hide()
            number = 1
            for new in self.data:
                if new==PokeNumber:
                    self.searchwidget = self.Pokemon_widget(self.data,new,number,True)
                    self.moi=number
                number+=1
            self.main_layout.addWidget(self.searchwidget)
    #fonction description
    
    def Pokemon_widget(self,data,test,number,check):
        if check != True:
            key = test
        else :
            key = f"{test}A"
        widget = QWidget()
        layout = QVBoxLayout(widget)
        url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{number:03d}.png"  # Formatage à 3 chiffres
        response = requests.get(url)
        response.raise_for_status()
        pixmapvalue = QPixmap()
        pixmapvalue.loadFromData(response.content)  # Chargement des données dans le pixmap
        self.keepPixmap[key]= pixmapvalue
        # Configuration du QLabel
        labelvalue= QLabel(self)
        labelvalue.setPixmap(pixmapvalue)
        labelvalue.setScaledContents(True)
        labelvalue.setFixedSize(100, 100)

        # Bouton pour le Pokémon
        button = QPushButton(data[test]["name"])
        button.clicked.connect(lambda _, t=test, px=pixmapvalue: self.validate_inputs(t, px))
        button.setMaximumSize(QSize(100, 20))
        #Numero Poke
        numlabel=QLabel(self)
        numlabel.setText(f"#{number:04d}")
        numlabel.setFont(QFont("Tahoma", 7, QFont.Bold))
        numlabel.setMaximumSize(QSize(100,7))
        # Ajout des widgets
        layout.addWidget(numlabel)
        layout.addWidget(labelvalue)
        layout.addWidget(button)
        self.labelValuelist[key]=labelvalue
        self.buttonlist[key]=button
        self.numlist[key]=numlabel  
        return widget
    
    def PokemonSuivant(self,Suivant,tag):
        if Suivant :
            self.msg_box.close()
            tag = int(tag.split('#')[1])+1
            tag=f'#{tag}'
            self.validate_inputs(tag,self.keepPixmap[tag])
        else : 
            self.msg_box.close()
            tag = int(tag.split('#')[1])-1
            tag=f'#{tag}'
            self.validate_inputs(tag,self.keepPixmap[tag])
    def validate_inputs(self,tag,pxmp):
        with open(f"{current_working_directory}\\Pokedex_descriptif.json",'r',encoding='utf-8') as file:
            data = json.load(file)
        Poketype= data[tag]['type']
        self.msg_box = QMessageBox(self)
        self.msg_box.setWindowTitle(f"Description {data[tag]['name']} ")
        self.msg_box.setText(f"{data[tag]['description']}")
        max_size = QSize(100, 100)
        pxmp = pxmp.scaled(max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.msg_box.setIconPixmap(pxmp)
        ###
        Poketype= data[tag]['type']
        UrlType= data['GlobalType'][Poketype]
        response_Poketype= requests.get(UrlType)
        response_Poketype.raise_for_status()
        pxmpe=QLabel()
        pxmpPoke = QPixmap()
        pxmpPoke.loadFromData(response_Poketype.content) 
        pxmpe.setPixmap(pxmpPoke)
        pxmpe.setScaledContents(True)
        pxmpe.setFixedSize(80, 16)
        layout = QHBoxLayout()
        layout.addWidget(pxmpe)
        custom_widget = QWidget()
        if data[tag]['type2']:
            Poketype2= data[tag]['type2']
            UrlType2= data['GlobalType'][Poketype2]
            response_Poketype2= requests.get(UrlType2)
            response_Poketype2.raise_for_status()
            pxmpe2=QLabel()
            pxmpPoke2 = QPixmap()
            pxmpPoke2.loadFromData(response_Poketype2.content) 
            pxmpe2.setPixmap(pxmpPoke2)
            pxmpe2.setScaledContents(True)
            pxmpe2.setFixedSize(80, 16)
            layout.addWidget(pxmpe2) 
        Suivantbutton = QPushButton(">")
        PrecedentButton = QPushButton("<")
        PrecedentButton.setFixedWidth
        PrecedentButton.clicked.connect(lambda :self.PokemonSuivant(False,tag))
        Suivantbutton.clicked.connect(lambda :self.PokemonSuivant(True,tag))
        custom_widget.setLayout(layout)
        self.msg_box.layout().addWidget(custom_widget)
        if int(tag.split('#')[1]) > 1:
            self.msg_box.layout().addWidget(PrecedentButton)
            PrecedentButton.setFixedSize(80,16)
        self.msg_box.layout().addWidget(Suivantbutton)
        Suivantbutton.setFixedSize(80,16)
        self.msg_box.exec()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())    