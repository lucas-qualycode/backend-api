run:
	firebase emulators:start --import ./firestore-snapshot --export-on-exit ./firestore-snapshot

deploy:
	firebase deploy --only functions
