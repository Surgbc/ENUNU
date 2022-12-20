debs:
	rm -rf installer
	mkdir -p installer/enunu_amd64/opt/enunu/
	mkdir -p installer/enunu_amd64/DEBIAN/
	cp -r synthesis installer/enunu_amd64/opt/enunu/
	cp enunu_server.sh installer/enunu_amd64/opt/enunu/
	cp requirements.txt installer/enunu_amd64/opt/enunu/
	cp -r pysinsy installer/enunu_amd64/opt/enunu/
	cp deb/p* installer/enunu_amd64/DEBIAN/
	cp -r lib installer/enunu_amd64/

	cp -r installer/enunu_amd64 installer/enunu_i386
	cp -r installer/enunu_amd64 installer/enunu_arm64

	cp deb/control_amd64/* installer/enunu_amd64/DEBIAN/
	dpkg-deb --build --root-owner-group installer/enunu_amd64

	cp deb/control_i386/* installer/enunu_i386/DEBIAN/
	dpkg-deb --build --root-owner-group installer/enunu_i386

	cp deb/control_arm64/* installer/enunu_arm64/DEBIAN/
	dpkg-deb --build --root-owner-group installer/enunu_arm64