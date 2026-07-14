import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DialogEditContact } from './dialog-edit-contact';

describe('DialogEditContact', () => {
  let component: DialogEditContact;
  let fixture: ComponentFixture<DialogEditContact>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DialogEditContact]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DialogEditContact);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
