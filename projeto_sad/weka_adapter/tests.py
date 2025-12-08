"""
weka_adapter/tests.py
Testes unitários para o adaptador WEKA
"""
from django.test import TestCase, Client
from django.urls import reverse
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from .services import WekaClassificationService
from .adapters import WekaAdapter


class WekaAdapterTest(TestCase):
    """Testes para o adaptador WEKA."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.adapter = WekaAdapter()
        self.service = WekaClassificationService()
        self.client = Client()
    
    def test_adapter_initialization(self):
        """Testa inicialização do adaptador."""
        self.assertIsNotNone(self.adapter)
        self.assertIsInstance(self.adapter.weka_classes, list)
        self.assertGreaterEqual(len(self.adapter.weka_classes), 4)
    
    def test_check_system_simulated(self):
        """Testa verificação do sistema em modo simulado."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = FileNotFoundError()
            status = self.adapter.check_system()
            
            self.assertIn('java_available', status)
            self.assertIn('weka_available', status)
            self.assertIn('model_exists', status)
            self.assertEqual(status['mode'], 'simulated')
    
    def test_create_arff_file(self):
        """Testa criação de arquivo ARFF."""
        features = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        
        try:
            arff_file = self.adapter.create_arff_file(features)
            self.assertTrue(os.path.exists(arff_file))
            
            # Verificar conteúdo
            with open(arff_file, 'r') as f:
                content = f.read()
                self.assertIn('@relation', content)
                self.assertIn('@data', content)
            
            # Limpar
            os.unlink(arff_file)
        except Exception as e:
            self.fail(f"Falha ao criar arquivo ARFF: {e}")
    
    def test_simulated_classification(self):
        """Testa classificação simulada."""
        features = [[36.5, 0.8, 36.0, 37.0, 37.5, 36.0, 36.8, 0.64, 0.3]]
        
        # Mock check_system para retornar modo simulado
        with patch.object(self.adapter, 'check_system') as mock_check:
            mock_check.return_value = {'system_ready': False, 'mode': 'simulated'}
            
            results = self.adapter.classify(features)
            
            self.assertGreater(len(results), 0)
            result = results[0]
            self.assertIn('predicted_class', result)
            self.assertIn('confidence', result)
            self.assertEqual(result['weka_mode'], 'simulated')
    
    @patch('subprocess.run')
    def test_real_classification_mocked(self, mock_subprocess):
        """Testa classificação real com mock."""
        # Configurar mock para simular WEKA disponível
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = """
        === Evaluation on test set ===
        inst#     actual  predicted error prediction
          1        2:?     1:NORMAL       0.95 (0.95/0.02/0.02/0.01)
        """
        mock_subprocess.return_value = mock_process
        
        # Mock check_system para retornar modo real
        with patch.object(self.adapter, 'check_system') as mock_check:
            mock_check.return_value = {
                'system_ready': True,
                'mode': 'real',
                'java_available': True,
                'weka_available': True,
                'model_exists': True
            }
            
            features = [[36.5, 0.8, 36.0, 37.0, 37.5, 36.0, 36.8, 0.64, 0.3]]
            results = self.adapter.classify(features)
            
            self.assertGreater(len(results), 0)


class WekaServiceTest(TestCase):
    """Testes para o serviço de classificação."""
    
    def setUp(self):
        self.service = WekaClassificationService()
    
    def test_service_initialization(self):
        """Testa inicialização do serviço."""
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.adapter)
    
    def test_extract_simulated_features(self):
        """Testa extração de características simuladas."""
        features = self.service._extract_simulated_features("test_image_normal.jpg")
        
        self.assertEqual(len(features), 9)
        self.assertIsInstance(features, list)
        self.assertTrue(all(isinstance(f, float) for f in features))
    
    def test_classify_image_simulated(self):
        """Testa classificação de imagem simulada."""
        # Criar arquivo temporário para teste
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'test image content')
            tmp_path = tmp_file.name
        
        try:
            # Mock adapter para usar modo simulado
            with patch.object(self.service.adapter, 'classify') as mock_classify:
                mock_classify.return_value = [{
                    'predicted_class': 'NORMAL',
                    'confidence': 0.85,
                    'confidence_percentage': 85.0,
                    'weka_mode': 'simulated',
                    'processing_time': 0.5
                }]
                
                result = self.service.classify_image(tmp_path)
                
                self.assertTrue(result['success'])
                self.assertEqual(result['predicted_class'], 'NORMAL')
                self.assertEqual(result['weka_mode'], 'simulated')
                self.assertIn('diagnosis_report', result)
        finally:
            # Limpar arquivo temporário
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class WekaViewsTest(TestCase):
    """Testes para as views da API."""
    
    def setUp(self):
        self.client = Client()
    
    def test_classify_endpoint_get(self):
        """Testa endpoint GET /classify/."""
        response = self.client.get(reverse('classify_image'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('endpoints', data)
    
    @patch.object(WekaClassificationService, 'classify_uploaded_image')
    def test_classify_endpoint_post_file(self, mock_classify):
        """Testa endpoint POST /classify/ com arquivo."""
        # Configurar mock
        mock_classify.return_value = {
            'success': True,
            'predicted_class': 'NORMAL',
            'confidence_percentage': 85.5,
            'weka_mode': 'simulated'
        }
        
        # Criar arquivo temporário para upload
        with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp_file:
            tmp_file.write(b'test image content')
            tmp_file.seek(0)
            
            response = self.client.post(
                reverse('classify_image'),
                {'image': tmp_file},
                format='multipart'
            )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['predicted_class'], 'NORMAL')
    
    @patch.object(WekaClassificationService, 'classify_image')
    def test_classify_endpoint_post_json(self, mock_classify):
        """Testa endpoint POST /classify/ com JSON."""
        # Configurar mock
        mock_classify.return_value = {
            'success': True,
            'predicted_class': 'BENIGNO',
            'confidence_percentage': 72.3,
            'weka_mode': 'real'
        }
        
        response = self.client.post(
            reverse('classify_image'),
            data=json.dumps({'image_path': '/path/to/image.jpg'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['predicted_class'], 'BENIGNO')
    
    def test_batch_endpoint(self):
        """Testa endpoint de classificação em lote."""
        response = self.client.post(
            reverse('batch_classification'),
            data=json.dumps({
                'image_paths': [
                    '/path/to/image1.jpg',
                    '/path/to/image2.jpg'
                ]
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
    
    def test_invalid_json(self):
        """Testa requisição com JSON inválido."""
        response = self.client.post(
            reverse('classify_image'),
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
    
    def test_missing_data(self):
        """Testa requisição sem dados."""
        response = self.client.post(
            reverse('classify_image'),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')


# Testes de integração (opcional)
class WekaIntegrationTest(TestCase):
    """Testes de integração para fluxos completos."""
    
    def test_complete_classification_flow(self):
        """Testa fluxo completo de classificação."""
        # Criar imagem de teste
        test_image_data = b'fake image data'
        
        with patch('weka_adapter.services.WekaClassificationService.extract_features') as mock_extract:
            with patch('weka_adapter.services.WekaAdapter.classify') as mock_classify:
                # Configurar mocks
                mock_extract.return_value = [36.5, 0.8, 36.0, 37.0, 37.5, 36.0, 36.8, 0.64, 0.3]
                mock_classify.return_value = [{
                    'instance': 1,
                    'predicted_class': 'NORMAL',
                    'confidence': 0.92,
                    'confidence_percentage': 92.0,
                    'distribution': {'NORMAL': 0.92, 'BENIGNO': 0.05, 'CISTO': 0.02, 'MALIGNO': 0.01},
                    'weka_mode': 'simulated',
                    'success': True
                }]
                
                # Executar fluxo
                service = WekaClassificationService()
                result = service.classify_image('/fake/path/image.jpg')
                
                # Verificar resultado
                self.assertTrue(result['success'])
                self.assertEqual(result['predicted_class'], 'NORMAL')
                self.assertGreater(result['confidence_percentage'], 90)
                self.assertIn('diagnosis_report', result)
    
    def test_error_handling(self):
        """Testa tratamento de erros."""
        with patch('weka_adapter.services.WekaClassificationService.extract_features') as mock_extract:
            mock_extract.side_effect = Exception("Erro simulado na extração")
            
            service = WekaClassificationService()
            result = service.classify_image('/fake/path/image.jpg')
            
            self.assertFalse(result['success'])
            self.assertIn('error', result)
            self.assertIn('Erro simulado', result['error'])
