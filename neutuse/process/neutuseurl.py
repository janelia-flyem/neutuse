from abc import ABCMeta,abstractmethod
from urllib.parse import urljoin


class NeutuseUrl():
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_service_registration_url(self, base_addr):
        pass
    
    @abstractmethod
    def get_service_pulse_url(self, base_addr):
        pass
        
    @abstractmethod
    def get_task_comment_url(self, base_addr):
        pass

    @abstractmethod
    def get_task_ack_url(self, base_addr, service_id):
        pass
        
    @abstractmethod
    def get_task_success_url(self, base_addr):
        pass
        
    @abstractmethod
    def get_task_fail_url(self, base_addr):
        pass
        
    @abstractmethod
    def get_task_topk_url(self, base_addr, type_, name, k):
        pass
        
    @abstractmethod
    def get_service_url(self, base_addr, service_id):
        pass
        
        
class NeutuseUrlV1(NeutuseUrl):

    def get_service_registration_url(self, base_addr):
        return urljoin(base_addr,'api/v1/services')
    
    def get_service_pulse_url(self, base_addr, service_id):
        return urljoin(base_addr,'/api/v1/services/{}/pulse'.format(service_id))

    def get_task_comment_url(self, base_addr, task_id):
        return urljoin(base_addr,'/api/v1/tasks/{}/comments'.format(task_id))

    def get_task_ack_url(self, base_addr, task_id, service_id):
        return urljoin(base_addr, '/api/v1/tasks/{}/status/processing/{}'.format(task_id, service_id))
        
    def get_task_success_url(self, base_addr, task_id, service_id):
        return urljoin(base_addr, '/api/v1/tasks/{}/status/done/{}'.format(task_id, service_id))
        
    def get_task_fail_url(self, base_addr, task_id, service_id):
       return urljoin(base_addr, '/api/v1/tasks/{}/status/failed/{}'.format(task_id, service_id))
        
    def get_task_topk_url(self, base_addr, type_, name, k):
        return urljoin(base_addr,'/api/v1/tasks/top/{}/{}/{}'.format(type_, name, k))
        
    def get_service_url(self, base_addr, service_id):
        return urljoin(base_addr,'/api/v1/services/{}'.format(service_id))
        
neutuse_url = NeutuseUrlV1()
