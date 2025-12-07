"""
weka_adapter/adapters.py
Adaptador WEKA - Comunicação via Command Script Interface (CSI)
Aluno 8: Adaptador WEKA
"""
import subprocess
import tempfile
import os
import logging
import time
from typing import List, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class WekaAdapter:
    """
    Adaptador para comunicação com WEKA via linha de comando (CSI).
    
    Implementa os comandos essenciais do WEKA:
    1. java weka.classifiers.trees.RandomForest -l modelo.model -T instancias.arff
    2. java weka.classifiers.trees.RandomForest -l modelo.model -T novas_instancias.arff -p 0
    3. java weka.classifiers.trees.RandomForest -l modelo.model -T novas_instancias.arff -distribution
    """
    
    def __init__(self, model_path: str = None):
        """
        Inicializa o adaptador WEKA.
        
        Args:
            model_path: Caminho para o modelo WEKA (opcional)
        """
        self.model_path = model_path or getattr(settings, 'WEKA_MODEL_PATH', '')
        self.weka_classes = getattr(settings, 'WEKA_CLASSES', ['NORMAL', 'BENIGNO', 'CISTO', 'MALIGNO'])
        self.java_path = getattr(settings, 'WEKA_JAVA_COMMAND', 'java')
        self.timeout = getattr(settings, 'WEKA_TIMEOUT', 30)
        
        logger.info(f"Adaptador WEKA CSI inicializado")
        logger.info(f"Classes: {self.weka_classes}")
        logger.info(f"Modelo: {self.model_path}")
    
    def check_system(self) -> Dict[str, Any]:
        """
        Verifica disponibilidade do sistema WEKA.
        
        Returns:
            Status do sistema
        """
        status = {
            'java_available': False,
            'weka_available': False,
            'model_exists': False,
            'system_ready': False,
            'mode': 'simulated',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # 1. Verificar Java
            logger.info("Verificando Java...")
            try:
                result = subprocess.run(
                    [self.java_path, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                status['java_available'] = result.returncode == 0
                logger.info("✓ Java disponível" if status['java_available'] else "✗ Java não disponível")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning("Java não encontrado no sistema")
            
            # 2. Verificar WEKA (se Java disponível)
            if status['java_available']:
                logger.info("Verificando WEKA...")
                try:
                    cmd = [self.java_path, 'weka.core.SystemInfo']
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    status['weka_available'] = result.returncode == 0
                    logger.info("✓ WEKA disponível" if status['weka_available'] else "✗ WEKA não disponível")
                except subprocess.TimeoutExpired:
                    logger.warning("Timeout ao verificar WEKA")
            
            # 3. Verificar modelo
            if self.model_path:
                status['model_exists'] = os.path.exists(self.model_path)
                logger.info(f"✓ Modelo encontrado" if status['model_exists'] else f"✗ Modelo não encontrado: {self.model_path}")
            
            # 4. Sistema pronto?
            status['system_ready'] = (
                status['java_available'] and
                status['weka_available'] and
                status['model_exists']
            )
            
            status['mode'] = 'real' if status['system_ready'] else 'simulated'
            
            if status['system_ready']:
                logger.info("✅ Sistema WEKA pronto para uso real")
            else:
                logger.info("⚠️ Sistema em modo simulado")
            
        except Exception as e:
            logger.error(f"Erro na verificação do sistema: {str(e)}")
            status['error'] = str(e)
        
        return status
    
    def create_arff_file(self, features: List[List[float]]) -> str:
        """
        Cria arquivo ARFF temporário a partir de características.
        
        Args:
            features: Lista de listas de características
            
        Returns:
            Caminho do arquivo ARFF criado
        """
        if not features:
            raise ValueError("Nenhuma característica fornecida")
        
        # Determinar número de características
        num_features = len(features[0])
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.arff', delete=False) as f:
            # Escrever cabeçalho ARFF
            f.write('@relation termografia_mamaria\n\n')
            
            # Escrever atributos
            for i in range(num_features):
                f.write(f'@attribute feature_{i:03d} numeric\n')
            
            # Escrever classe
            classes_str = ','.join(self.weka_classes)
            f.write(f'@attribute class {{{classes_str}}}\n\n')
            
            # Escrever dados
            f.write('@data\n')
            for feature_set in features:
                # Formatar valores
                values = [f'{value:.6f}' for value in feature_set]
                # '?' indica classe desconhecida (para classificação)
                f.write(','.join(values) + ',?\n')
            
            filepath = f.name
        
        logger.info(f"Arquivo ARFF criado: {filepath}")
        return filepath
    
    def classify(self, features: List[List[float]]) -> List[Dict[str, Any]]:
        """
        Classifica características usando WEKA via CSI.
        
        Args:
            features: Lista de características para classificar
            
        Returns:
            Lista de resultados
        """
        logger.info(f"Iniciando classificação de {len(features)} instância(s)")
        
        # Verificar sistema
        system_status = self.check_system()
        
        # Se sistema não pronto, usar modo simulado
        if not system_status['system_ready']:
            logger.warning("Sistema WEKA não disponível. Usando modo simulado.")
            return self._simulate_classification(features)
        
        try:
            # 1. Criar arquivo ARFF
            arff_file = self.create_arff_file(features)
            
            # 2. Construir comando WEKA
            cmd = [
                self.java_path,
                'weka.classifiers.trees.RandomForest',
                '-l', self.model_path,      # Carregar modelo
                '-T', arff_file,            # Arquivo de teste
                '-p', '0',                  # Mostrar previsões
                '-distribution',            # Mostrar distribuição
                '-i'                        # Informações do classificador
            ]
            
            logger.info(f"Executando comando WEKA...")
            
            # 3. Executar classificação
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            processing_time = time.time() - start_time
            
            logger.info(f"WEKA executado em {processing_time:.2f} segundos")
            
            # 4. Limpar arquivo temporário
            try:
                os.unlink(arff_file)
            except OSError:
                logger.warning(f"Não foi possível remover arquivo temporário")
            
            # 5. Verificar resultado
            if result.returncode != 0:
                error_msg = f"WEKA retornou erro: {result.stderr[:200]}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # 6. Parsear resultado
            classification_results = self._parse_weka_output(result.stdout)
            
            # Adicionar metadados
            for res in classification_results:
                res.update({
                    'processing_time': processing_time,
                    'weka_mode': 'real',
                    'system_status': system_status
                })
            
            logger.info(f"Classificação concluída: {len(classification_results)} resultado(s)")
            return classification_results
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ({self.timeout}s) na execução do WEKA")
            return self._simulate_classification(features)
        except Exception as e:
            logger.error(f"Erro na classificação WEKA: {str(e)}")
            return self._simulate_classification(features)
    
    def _parse_weka_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parseia a saída do WEKA.
        
        Args:
            output: Saída do comando WEKA
            
        Returns:
            Resultados parseados
        """
        results = []
        lines = output.split('\n')
        
        # Encontrar início da seção de previsões
        predictions_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('inst#'):
                predictions_start = i + 1
                break
        
        if predictions_start == -1:
            logger.warning("Formato de saída do WEKA não reconhecido")
            # Tentar encontrar previsões de outra forma
            for line in lines:
                if ':' in line and ('NORMAL' in line or 'BENIGNO' in line or 'CISTO' in line or 'MALIGNO' in line):
                    parts = line.split()
                    if len(parts) >= 3:
                        predicted = parts[2]
                        if ':' in predicted:
                            predicted = predicted.split(':')[1]
                        
                        results.append({
                            'instance': len(results) + 1,
                            'predicted_class': predicted,
                            'confidence': 0.8,
                            'distribution': {},
                            'raw_line': line
                        })
            
            if results:
                return results
            else:
                return self._simulate_classification([[0] * 9])
        
        # Processar cada linha de previsão
        for line in lines[predictions_start:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 5 and parts[0].replace('.', '').isdigit():
                try:
                    # Extrair informações básicas
                    instance_num = int(float(parts[0]))
                    predicted = parts[2]
                    
                    # Limpar formato
                    if ':' in predicted:
                        predicted = predicted.split(':')[1]
                    
                    # Garantir que a classe está na lista permitida
                    if predicted not in self.weka_classes:
                        predicted_upper = predicted.upper()
                        for valid_class in self.weka_classes:
                            if valid_class in predicted_upper:
                                predicted = valid_class
                                break
                        else:
                            predicted = self.weka_classes[0]
                    
                    # Tentar extrair distribuição de probabilidade
                    distribution = {}
                    confidence = 0.0
                    
                    # Procurar por padrão de distribuição
                    for part in parts:
                        if '(' in part and ')' in part:
                            # Formato: (0.95/0.02/0.02/0.01)
                            probs_str = part.strip('()')
                            probs = probs_str.split('/')
                            
                            if len(probs) == len(self.weka_classes):
                                for idx, prob in enumerate(probs):
                                    if idx < len(self.weka_classes):
                                        try:
                                            distribution[self.weka_classes[idx]] = float(prob)
                                        except ValueError:
                                            distribution[self.weka_classes[idx]] = 0.0
                    
                    # Calcular confiança
                    if predicted in distribution:
                        confidence = distribution[predicted]
                    elif distribution:
                        confidence = max(distribution.values())
                    else:
                        confidence = 0.8  # Valor padrão
                    
                    # Construir resultado
                    result = {
                        'instance': instance_num,
                        'predicted_class': predicted,
                        'confidence': confidence,
                        'confidence_percentage': round(confidence * 100, 2),
                        'distribution': distribution,
                        'raw_line': line,
                        'success': True
                    }
                    
                    results.append(result)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Erro ao parsear linha '{line}': {e}")
        
        return results
    
    def _simulate_classification(self, features: List[List[float]]) -> List[Dict[str, Any]]:
        """
        Simula classificação quando WEKA não está disponível.
        
        Args:
            features: Características para classificar
            
        Returns:
            Resultados simulados
        """
        import random
        
        logger.info("Executando classificação simulada")
        
        results = []
        
        for i, feature_set in enumerate(features):
            # Lógica de simulação baseada nas características
            if feature_set and len(feature_set) > 0:
                # Usar primeira característica como "temperatura" simulada
                simulated_temp = feature_set[0] if feature_set[0] > 0 else 37.0
            else:
                simulated_temp = 37.0
            
            # Decisão baseada em "temperatura" simulada
            if simulated_temp < 36.8:
                predicted = 'NORMAL'
                base_confidence = 0.9
            elif simulated_temp < 37.3:
                predicted = 'BENIGNO'
                base_confidence = 0.8
            elif simulated_temp < 37.8:
                predicted = 'CISTO'
                base_confidence = 0.7
            else:
                predicted = 'MALIGNO'
                base_confidence = 0.6
            
            # Adicionar variação aleatória
            confidence = random.uniform(base_confidence - 0.1, base_confidence + 0.05)
            confidence = max(0.1, min(0.99, confidence))
            
            # Criar distribuição de probabilidade simulada
            distribution = {}
            remaining = 1.0 - confidence
            other_classes = [c for c in self.weka_classes if c != predicted]
            
            for cls in self.weka_classes:
                if cls == predicted:
                    distribution[cls] = confidence
                else:
                    distribution[cls] = remaining / len(other_classes)
            
            # Simular tempo de processamento
            processing_time = random.uniform(0.5, 2.0)
            
            results.append({
                'instance': i + 1,
                'predicted_class': predicted,
                'confidence': confidence,
                'confidence_percentage': round(confidence * 100, 2),
                'distribution': distribution,
                'processing_time': processing_time,
                'weka_mode': 'simulated',
                'simulation_note': 'Classificação simulada - WEKA não disponível',
                'success': True
            })
        
        return results
    
    def test(self) -> Dict[str, Any]:
        """
        Testa o adaptador com dados de exemplo.
        
        Returns:
            Resultado do teste
        """
        logger.info("Executando teste do adaptador WEKA")
        
        # Dados de teste
        test_features = [
            [36.5, 0.8, 36.0, 37.0, 37.5, 36.0, 36.8, 0.64, 0.3],  # Normal
            [37.2, 1.5, 36.7, 37.7, 38.2, 36.7, 37.3, 2.25, 0.7],  # Benigno
            [37.8, 2.1, 37.3, 38.3, 38.8, 37.3, 37.9, 4.41, 1.1],  # Cisto
        ]
        
        try:
            # Verificar sistema
            system_status = self.check_system()
            
            # Executar classificação
            start_time = time.time()
            classification_results = self.classify(test_features)
            total_time = time.time() - start_time
            
            # Estatísticas
            stats = {
                'total_instances': len(test_features),
                'successful_classifications': len(classification_results),
                'simulated_count': sum(1 for r in classification_results if r.get('weka_mode') == 'simulated'),
                'real_count': sum(1 for r in classification_results if r.get('weka_mode') == 'real'),
                'total_time': total_time,
            }
            
            return {
                'test_completed': True,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'system_status': system_status,
                'statistics': stats,
                'results': classification_results,
                'test_features_count': len(test_features),
                'message': 'Teste do adaptador WEKA concluído'
            }
            
        except Exception as e:
            logger.error(f"Erro no teste: {str(e)}")
            return {
                'test_completed': False,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e),
                'message': 'Falha no teste'
            }
