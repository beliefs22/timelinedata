import pulltimeline_working


def main():
    directories = pulltimeline_working.getipdata.process.getDirectories()
    ip_subject_files_dir = directories['IP Subject Dir']
    pulltimeline_working.getipdata.getLabs(ip_subject_files_dir)
    pulltimeline_working.getipdata.getMeds(ip_subject_files_dir)
    pulltimeline_working.getipdata.getVitals(ip_subject_files_dir)

if __name__ == "__main__":
    main()
