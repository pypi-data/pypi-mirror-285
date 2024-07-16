import glob
import os
import os.path as osp


class Deployment:
    """
    Deploy or delete a plugin to a game project.
    """
    def __init__(self, name, project_root):
        self.name = name
        self.projectRoot = project_root
        self.pluginDeployDir = ''

    @staticmethod
    def create(name, project_root: str = ''):
        if glob.glob(osp.join(project_root, '*.uproject')):
            print('Target: UE project detected.')
            return UEDeployment(name, project_root)
        raise NotImplementedError(f'Not implemented for this target, currently only supports UE.')

    def deploy(self, target: str):
        print(f"Deploying {self.name}...")

    def delete(self, target: str):
        print(f"Deleting {self.name}...")
        fs = glob.glob(rf'{self.pluginDeployDir}\**\*{self.name}*',
                       recursive=True)
        for f in fs:
            os.remove(f)


class UEDeployment(Deployment):
    def __init__(self, name, project_root):
        super().__init__(name, project_root)
        self.pluginDeployDir = osp.join(self.projectRoot, 'Plugins', 'Wwise', 'ThirdParty')
