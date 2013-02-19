import os
from shutil import copyfile
import ConfigParser
from olcmodules.config import PROFILES_PATH

class profile(object):
    def __init__(self):
        self._cp = ConfigParser.ConfigParser()
        self._main_sections = {'olfc':{},'names':{},'packages':{},'firmware':{}}
        self._profile_contents = {}

        self._profile_path = ''
        self._default_cfg_name = 'default.cfg'
        self._default_profile_path = os.path.join(PROFILES_PATH, self._default_cfg_name)


    def error(self, e):
        assert False, e


    def _get_option(self, section, option):
        try:
            return self._cp.get(section, option)            
        except ConfigParser.Error, e:
            return False


    def _get_section(self, section):
        try:
            return self._cp.items(section)
        except ConfigParser.Error, e:
            return False



    def _verify(self, path):
        error = False

        for section in self._main_sections:
            if not self._get_section(section):
                error = True
                break

        if error:
            return False
        else:
            return True

    
    def current_profile_name(self):
        return os.path.basename(self._profile_path)


    def get_profile(self):
        if len(self._profile_contents) == 0:
            for section_name in self._main_sections:
                self._profile_contents[section_name] = {}
                options_list = self._get_section(section_name)

                for option in options_list:
                    self._profile_contents[section_name][option[0]] = option[1]
                
                    if section_name == 'firmware' and option[0] == 'firmware_names':
                        fw_files_info = {}
                        fw_file_name_list = option[1].split(',')
                       
                        for fw_file_name in fw_file_name_list:
                            fw_files_info[fw_file_name] = {}
                            fw_file_info = self._get_section(fw_file_name)

                            for fw_file_info_entry in fw_file_info:
                                fw_files_info[fw_file_name][fw_file_info_entry[0]] = fw_file_info_entry[1]

                        self._profile_contents[section_name]['firmware_file_info'] = fw_files_info
 
        return self._profile_contents



    def load_profile(self, path=False):
        if not path:
            profile_path = self._default_profile_path
        else:
            profile_path = path

        try:
            if profile_path == self._cp.read(profile_path)[0]:
                
                if self._verify(profile_path):
                    self._profile_contents = {}
                    self.profile_path = profile_path
                else:
                    self.error('Does not appear to be a valid profile config file.')
            else:
                self.error('Profile path does not exist.')
        except ConfigParser.Error, e:
            self.error(e)


    def save_as_default(self):
        try:
            if self._profile_path:
                copyfile(self._profile_path, self._default_profile_path)
            else:
                self.error('No device profile set to save as default.')
        except Exception, e:
            self.error(e)

if __name__ == '__main__':
    # requires a few path adjustments
    # prints cfg file dict
    from pprint import pprint
    dp = profile()
    dp.load_profile()
    pprint(dp.get_profile())