from firebase_admin import firestore


def save_user_data(db, phone_number, data):
    try:
        doc_ref = db.collection("users").document(phone_number)
        doc_ref.set(data, merge=True)
        return True

    except Exception as err:
        return False


def read_user_data(db, phone_number):
    try:
        doc_ref = db.collection("users").document(phone_number)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    except Exception as err:
        return None
