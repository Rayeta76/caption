"""
Extractor de keywords usando YAKE
Extrae palabras clave relevantes de texto en español e inglés
"""
import yake
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class KeywordExtractor:
    """Extractor de keywords inteligente usando YAKE"""
    
    def __init__(self, language="es", max_keywords=10):
        """
        Inicializa el extractor
        
        Args:
            language: Idioma ('es' para español, 'en' para inglés)
            max_keywords: Máximo número de keywords a extraer
        """
        self.language = language
        self.max_keywords = max_keywords
        
        # Configuración de YAKE
        self.kw_extractor = yake.KeywordExtractor(
            lan=language,
            n=3,  # Máximo de palabras por keyword
            dedupLim=0.7,  # Límite de deduplicación
            top=max_keywords,  # Top keywords
            features=None
        )
        
        # Palabras vacías adicionales en español
        self.spanish_stopwords = {
            'imagen', 'foto', 'fotografía', 'picture', 'image', 'esta', 'este', 
            'esa', 'ese', 'aquí', 'allí', 'donde', 'cuando', 'como', 'muy',
            'más', 'menos', 'sobre', 'bajo', 'entre', 'dentro', 'fuera'
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extrae keywords del texto dado
        
        Args:
            text: Texto del cual extraer keywords
            
        Returns:
            Lista de keywords extraídas
        """
        if not text or not text.strip():
            return []
        
        try:
            # Limpiar texto
            cleaned_text = self._clean_text(text)
            
            # Extraer keywords con YAKE
            keywords = self.kw_extractor.extract_keywords(cleaned_text)
            
            # Filtrar y procesar keywords
            filtered_keywords = self._filter_keywords(keywords)
            
            return filtered_keywords
            
        except Exception as e:
            logger.error(f"Error extrayendo keywords: {e}")
            return self._fallback_extraction(text)
    
    def _clean_text(self, text: str) -> str:
        """Limpia el texto para mejor extracción"""
        # Remover caracteres especiales pero mantener espacios
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _filter_keywords(self, keywords: List[Tuple[float, str]]) -> List[str]:
        """Filtra y procesa las keywords extraídas"""
        filtered = []
        
        for item in keywords:
            # YAKE devuelve (keyword, score)
            if isinstance(item, tuple) and len(item) == 2:
                keyword, score = item
            else:
                # Fallback si el formato es diferente
                keyword = str(item)
            
            # Limpiar keyword
            keyword = str(keyword).lower().strip()
            
            # Filtros de calidad
            if (len(keyword) < 3 or  # Muy corta
                len(keyword) > 30 or  # Muy larga
                keyword.isdigit() or  # Solo números
                keyword in self.spanish_stopwords or  # Palabra vacía
                any(char.isdigit() for char in keyword) and len(keyword) < 5):  # Números cortos
                continue
            
            # Capitalizar primera letra
            keyword = keyword.capitalize()
            
            if keyword not in filtered:
                filtered.append(keyword)
        
        return filtered[:self.max_keywords]
    
    def _fallback_extraction(self, text: str) -> List[str]:
        """Extracción de respaldo si YAKE falla"""
        try:
            # Extracción simple basada en frecuencia
            words = re.findall(r'\b[a-záéíóúñA-ZÁÉÍÓÚÑ]{4,}\b', text.lower())
            
            # Contar frecuencias
            word_freq = {}
            for word in words:
                if word not in self.spanish_stopwords:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Ordenar por frecuencia y tomar los top
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            return [word.capitalize() for word, _ in sorted_words[:self.max_keywords]]
            
        except Exception as e:
            logger.error(f"Error en extracción de respaldo: {e}")
            return []

def extract_keywords_from_text(text: str, language="es", max_keywords=10) -> List[str]:
    """
    Función de conveniencia para extraer keywords
    
    Args:
        text: Texto del cual extraer keywords
        language: Idioma ('es' o 'en')
        max_keywords: Máximo número de keywords
        
    Returns:
        Lista de keywords
    """
    extractor = KeywordExtractor(language=language, max_keywords=max_keywords)
    return extractor.extract_keywords(text) 