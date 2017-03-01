require 'spec_helper'

files = ['ceph.conf', 'cinder_uuid', 'fsid', 'rbdmap' ]
 files.each do |file|
  describe file("/etc/ceph/#{file}") do
    it { should be_owned_by 'root' }
    it { should be_grouped_into 'root' }
    it { should be_mode 644 }
  end
end

if File.exist?("/etc/logrotate.d/ceph")
  describe file('/etc/logrotate.d/ceph') do
    it { should exist }
    file_contents = [ '# Generated by Ansible.',
           '# Local modifications will be overwritten.',
           '',
           '/var/log/ceph/*.log',
           '{',
           'daily',
           'missingok',
           'rotate 7',
           'compress',
           '}']
    file_contents.each do |file_line|
      it { should contain file_line }
    end
  end
end

files = Dir['/var/log/ceph/grep log$']
files.each do |file|
  if File.exist?("/var/log/ceph/#{file}")
    describe file("/var/log/ceph/#{file}") do
      it { should be_owned_by 'root' }
      it { should be_grouped_into 'adm' }
      it { should be_mode 644 }
    end
  end
end
