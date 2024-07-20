from llama_index.multi_modal_llms.gemini import GeminiMultiModal
from llama_index.core.multi_modal_llms.generic_utils import load_image_urls
from llama_index.core import SimpleDirectoryReader
from json_extractor import extract, save_json_to_file
import time
from threading import Thread
import animation
from PIL import Image

PROMPT = """you are an ai that returns a time table in json format and in english from a given image
this is an example of how the output should look like:
```json	
{
  "Monday": {
    "08:30-10:00": {
      "IA1.1": {
        "course": "Reseaux informatiques (TP)",
        "instructor": "BEN FARAH Ahmed",
        "location": "I12"
      },
      "IA1.2": {
        "course": "Architecture des microprocesseurs et des multiprocesseurs (TP)",
        "instructor": "KHADRAOUI Imen",
        "location": "I13"
      }
    },
    "10:15-11:45": {
      "IA1.1": {
        "course": "Reseaux informatiques (TP)",
        "instructor": "BEN FARAH Ahmed",
        "location": "I12"
      },
      "IA1.2": {
        "course": "Architecture des microprocesseurs et des multiprocesseurs (TP)",
        "instructor": "KHADRAOUI Imen",
        "location": "I13"
      }
    },
    "12:00-13:00": {},
    "13:00-14:30": {
      "IA1.1": {
        "course": "Réseaux de Petri",
        "instructor": "ABDELLAOUI Mehrez",
        "location": "B02"
      }
    },
    "14:45-16:15": {
      "IA1.1": {
        "course": "Elements de puissance (1/15)",
        "instructor": "BEL HADJ IBRAHIM Anis",
        "location": "R03"
      }
    },
    "16:30-18:00": {}
  },
  "Tuesday": {
    "08:30-10:00": {
      "IA1.1": {
        "course": "Automatique lineaire echantillonne (TP)",
        "instructor": "BEMBILI Sana",
        "location": "E13"
      }
    },
    "10:15-11:45": {
      "IA1.1": {
        "course": "Automatique lineaire echantillonne (TP)",
        "instructor": "BEMBILI Sana",
        "location": "E13"
      }
    },
    "12:00-13:00": {},
    "13:00-14:30": {
      "IA1.2": {
        "course": "Programmation Orientee Objet",
        "instructor": "ABDELATTIF Takoua",
        "location": "B04"
      }
    },
    "14:45-16:15": {
      "IA1.2": {
        "course": "Elements de puissance",
        "instructor": "BEL HADJ IBRAHIM Anis",
        "location": "B04"
      }
    },
    "16:30-18:00": {}
  },
  "Wednesday": {
    "08:30-10:00": {
      "IA1.1": {
        "course": "Reseaux informatiques (1/15)",
        "instructor": "BEN ARBIA Anis",
        "location": ""
      }
    },
    "10:15-11:45": {
      "IA1.1": {
        "course": "Algorithmique et Structures de donnees II (1/15)",
        "instructor": "CHAINBI Walid",
        "location": "B04"
      }
    },
    "12:00-13:00": {},
    "13:00-14:30": {},
    "14:45-16:15": {},
    "16:30-18:00": {}
  },
  "Thursday": {
    "08:30-10:00": {
      "IA1.1": {
        "course": "Algorithmique et Structures de donnees II (1/15)",
        "instructor": "CHAINBI Walid",
        "location": "B04"
      }
    },
    "10:15-11:45": {
      "IA1.1": {
        "course": "Reseaux informatiques",
        "instructor": "BEN ARBIA Anis",
        "location": "R03"
      }
    },
    "12:00-13:00": {},
    "13:00-14:30": {
      "IA1.1": {
        "course": "Circuits Programmables (FPGA)",
        "instructor": "BOUZOUITA Badreddine",
        "location": "B11"
      }
    },
    "14:45-16:15": {
      "IA1.2": {
        "course": "Architecture des microprocesseurs et des\nmultiprocesseurs (1/15)",
        "instructor": "BRAHMI Nabiha",
        "location": "B11"
      }
    },
    "16:30-18:00": {}
  },
  "Friday": {
    "08:30-10:00": {
      "IA1.1": {
        "course": "Anglais II",
        "instructor": "RDIFI Eya",
        "location": "B12 (Labo\nAnglais)"
      },
      "IA1.2": {
        "course": "GTE1, IA1,\nIA2,\nProfessional\nCareer\nDevelopment",
        "instructor": "AYARA\nKhawla\nAmphi",
        "location": ""
      }
    },
    "10:15-11:45": {
      "IA1.1": {
        "course": "Circuits\nProgrammables\n(FPGA) (TP)",
        "instructor": "SOUILEM Haifa",
        "location": "E21"
      },
      "IA1.2": {
        "course": "Francais",
        "instructor": "CHEHIDI Latifa",
        "location": "A04 (Labo\nFrancais)"
      }
    },
    "12:00-13:00": {},
    "13:00-14:30": {
      "IA1.1": {
        "course": "Circuits\nProgrammables\n(FPGA) (TP)",
        "instructor": "SOUILEM Haifa",
        "location": "E21"
      }
    },
    "14:45-16:15": {
      "IA1.1": {
        "course": "Automatique\nlineaire\nechantillonne",
        "instructor": "SAAD Ihssen",
        "location": "R04"
      }
    },
    "16:30-18:00": {
      "IA1.1": {
        "course": "Probabilites et\nstatistiques",
        "instructor": "GHOZZI\nAouicha",
        "location": "R01"
      }
    }
  },
  "Saturday": {
    "08:30-10:00": {
      "IA1.1": {
        "course": "Anglais II",
        "instructor": "MABROUK\nRaouia",
        "location": "B13 (Labo\nAnglais)"
      },
      "IA1.2": {
        "course": "Programmation\nOrientee Objet\n(TP)",
        "instructor": "TRABELSI Salma",
        "location": "I21"
      }
    },
    "10:15-11:45": {
      "IA1.2": {
        "course": "Programmation\nOrientee Objet\n(TP)",
        "instructor": "TRABELSI Salma",
        "location": "I21"
      }
    },
    "12:00-13:00": {},
    "13:00-14:30": {},
    "14:45-16:15": {},
    "16:30-18:00": {}
  }
}
```	
"""

def generate_timetable(PATH:str,API_KEY:str)->None:
    """
    Generates a timetable in JSON format based on the provided prompt and image documents.

    Returns:
        None
    """
    
    try:
      with Image.open("images/test.png") as img:
        img.show()
    except Exception as e:
      print(f"Error opening image: {e}")
      
    Thread(target=animation.animate, daemon=True).start()
    
    # load image documents from local directory
    image_documents = SimpleDirectoryReader("images").load_data()

    mm_llm = GeminiMultiModal(model_name="models/gemini-1.5-pro", api_key=API_KEY)
    start = time.time()
    response = mm_llm.complete(
        prompt=PROMPT, image_documents=image_documents
    ).text
    end = time.time()

    print("Time taken: ", int(end-start),"sec \n","\n-------------------------\n" ,"Table generated!!")

    try:
        extracted_json = extract(response)
        save_json_to_file(extracted_json, PATH)
        print("\n-------------------------\nOutput saved to table.json!!")
    except Exception as e:
        print(f"Error extracting JSON content: {e}")

    